import json
from django.core.management.base import BaseCommand
from bopo_admin.models import State, City

class Command(BaseCommand):
    help = 'Load only Indian states and their cities from JSON files'

    def handle(self, *args, **kwargs):
        self.stdout.write("🧹 Cleaning up existing states and cities...")

        # First delete cities due to FK constraint
        City.objects.all().delete()
        State.objects.all().delete()

        # Load JSON data
        with open('E:\\BOPO\\bopo_backend\\bopo_admin\\data\\states.json', 'r', encoding='utf-8') as f:
            states_data = json.load(f)

        with open('E:\\BOPO\\bopo_backend\\bopo_admin\\data\\cities.json', 'r', encoding='utf-8') as f:
            cities_data = json.load(f)

        # 🔄 Filter only Indian states
        self.stdout.write("🔄 Filtering and loading Indian states...")
        indian_states = [state for state in states_data if state.get('country_name', '').lower() == 'india']


        inserted_states = []
        for state in indian_states:
            try:
                s, _ = State.objects.update_or_create(
                    id=state['id'],
                    defaults={'name': state['name']}
                )
                inserted_states.append(s.name)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️ Could not insert state {state['name']}: {e}"))

        self.stdout.write(f"✅ Inserted or updated {len(inserted_states)} Indian states.")

        # 🏙️ Insert only cities belonging to Indian states
        self.stdout.write("🏙️ Filtering and loading cities belonging to Indian states...")
        indian_state_ids = [state['id'] for state in indian_states]

        inserted_cities = 0
        for city in cities_data:
            if city['state_id'] in indian_state_ids:
                try:
                    state = State.objects.get(id=city['state_id'])
                    City.objects.update_or_create(
                        id=city['id'],
                        defaults={'name': city['name'], 'state': state}
                    )
                    inserted_cities += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"⚠️ Could not insert city {city['name']}: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"🎉 Successfully inserted or updated {len(inserted_states)} Indian states and {inserted_cities} cities!"
        ))
