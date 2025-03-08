import base64
from venv import logger
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Boycott, Alternateproducts

CATEGORY_MAPPING = {
    "Beverages": "Drinks",
    "Body Wash": "Washing detergent",
    # Add other mappings if needed
}

@csrf_exempt
def check_boycott(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"Received data: {data}")  # Debugging Log
            brand_name = data.get('brand', None)

            if brand_name:
                boycott_entry = Boycott.objects.filter(boycottcompanyname__icontains=brand_name).first()
                
                if boycott_entry:
                    response_data = {
                        'status': 'boycotted',
                        'message': f'The brand "{brand_name}" is boycotted due to: {boycott_entry.reason}.',
                        'country_of_manufacture': boycott_entry.countryofmanufacture
                    }

                    # Fetch alternative products related to the brand
                    alternative_products = Alternateproducts.objects.filter(alternateproductcompany__icontains=brand_name)

                    alternatives_list = []
                    for alt in alternative_products:
                        # Handle BinaryField for image
                        image_base64 = base64.b64encode(alt.alternateproductimage).decode('utf-8') if alt.alternateproductimage else None

                        alternatives_list.append({
                            'alternative_product': alt.alternateproductname,
                            'alternative_company': alt.alternatecompanyname,
                            'image_base64': image_base64  # Include Base64-encoded image
                        })

                    response_data['alternatives'] = alternatives_list if alternatives_list else 'No direct alternatives found.'
                else:
                    response_data = {
                        'status': 'not_boycotted',
                        'message': f'The brand "{brand_name}" is not boycotted.',
                    }
            else:
                response_data = {'status': 'error', 'message': 'No brand provided in the request.'}

        except json.JSONDecodeError:
            response_data = {'status': 'error', 'message': 'Invalid JSON format.'}

        return JsonResponse(response_data)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed.'})
    

# ✅ New View for Alternative Products by Category
@csrf_exempt
def get_alternatives(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_name = data.get('category', None)

            if category_name:
                # Use the mapping to translate the category name
                category_name = CATEGORY_MAPPING.get(category_name, category_name)

                # Fetch alternative products based on the mapped category
                alternative_products = Alternateproducts.objects.filter(
                    alternatecategory__categoryid__categoryname__icontains=category_name
                )

                alternatives_list = []
                for alt in alternative_products:
                    # Handle BinaryField for image
                    image_base64 = base64.b64encode(alt.alternateproductimage).decode('utf-8') if alt.alternateproductimage else None

                    alternatives_list.append({
                        'alternative_product': alt.alternateproductname,
                        'alternative_company': alt.alternatecompanyname,
                        'image_base64': image_base64
                    })

                return JsonResponse({'status': 'success', 'alternatives': alternatives_list})

            else:
                return JsonResponse({'status': 'error', 'message': 'No category provided.'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'})

    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed.'})
