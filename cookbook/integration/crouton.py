import json
from io import BytesIO
from zipfile import ZipFile
import base64

from cookbook.helper.image_processing import get_filetype
from cookbook.helper.ingredient_parser import IngredientParser
from cookbook.helper.recipe_url_import import parse_duration, parse_time, parse_servings
from cookbook.integration.integration import Integration
from cookbook.models import Ingredient, Keyword, NutritionInformation, Recipe, Step

class Crouton(Integration):

    def import_file_name_filter(self, zip_info_object):
        return zip_info_object.filename.endswith('.crumb')
    
    def get_recipe_from_file(self, file):
        recipe_json = json.loads(file.getvalue().decode("utf-8"))

        recipe = Recipe.objects.create(
            name=recipe_json['name'].strip(),
            created_by=self.request.user, internal=True, space=self.request.space)
        
        if 'serves' in recipe_json:
            recipe.servings = parse_servings(recipe_json['serves'])
        if 'duration' in recipe_json:
            recipe.working_time = parse_time(recipe_json['duration'])
        if 'cookDuration' in recipe_json:
            recipe.waiting_time = parse_time(recipe_json['cookDuration'])
        if 'webLink' in recipe_json:
            recipe.source_url = recipe_json['webLink']

        # FIXME: add category and tags as keywords


        if recipe_json.get("images", None):
            try:
                self.import_recipe_image(recipe, BytesIO(base64.b64decode(recipe_json['images'][0])), filetype='.PNG')
            except Exception:
                pass








        return super().get_recipe_from_file(file)