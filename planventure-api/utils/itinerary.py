from datetime import datetime, timedelta
import json

class ItineraryTemplate:
    """Utility class for generating default itinerary templates"""
    
    # Destination types and their characteristics
    DESTINATION_TYPES = {
        'city': {
            'activities': [
                'Walking tour of historic district',
                'Visit local museums',
                'Explore local markets',
                'Try traditional cuisine',
                'Visit cultural landmarks',
                'Shopping at local boutiques',
                'Evening entertainment/shows',
                'Photography tour',
                'Local art galleries',
                'Architecture tour'
            ],
            'morning_activities': [
                'Museum visit',
                'Walking tour',
                'Local breakfast spot',
                'Market exploration'
            ],
            'afternoon_activities': [
                'Landmark visits',
                'Shopping',
                'Cultural sites',
                'Local experiences'
            ],
            'evening_activities': [
                'Traditional dinner',
                'Evening shows',
                'Nightlife exploration',
                'Sunset viewing'
            ]
        },
        'beach': {
            'activities': [
                'Beach relaxation',
                'Water sports',
                'Snorkeling/diving',
                'Beach volleyball',
                'Sunset watching',
                'Seafood dining',
                'Coastal walks',
                'Beach photography',
                'Local fishing experience',
                'Island hopping'
            ],
            'morning_activities': [
                'Beach yoga',
                'Morning swim',
                'Beach walk',
                'Breakfast by the ocean'
            ],
            'afternoon_activities': [
                'Water sports',
                'Beach games',
                'Snorkeling',
                'Coastal exploration'
            ],
            'evening_activities': [
                'Sunset watching',
                'Seafood dinner',
                'Beach bonfire',
                'Coastal nightlife'
            ]
        },
        'mountain': {
            'activities': [
                'Hiking trails',
                'Mountain climbing',
                'Nature photography',
                'Wildlife watching',
                'Scenic viewpoints',
                'Local cuisine',
                'Mountain biking',
                'Stargazing',
                'Adventure sports',
                'Hot springs'
            ],
            'morning_activities': [
                'Early morning hike',
                'Sunrise viewing',
                'Mountain breakfast',
                'Nature walks'
            ],
            'afternoon_activities': [
                'Trail exploration',
                'Adventure activities',
                'Scenic drives',
                'Wildlife spotting'
            ],
            'evening_activities': [
                'Mountain lodge dinner',
                'Stargazing',
                'Campfire gathering',
                'Local mountain culture'
            ]
        },
        'cultural': {
            'activities': [
                'Historical site visits',
                'Museum tours',
                'Cultural performances',
                'Traditional workshops',
                'Religious sites',
                'Local festivals',
                'Art galleries',
                'Heritage walks',
                'Local craft markets',
                'Traditional food experiences'
            ],
            'morning_activities': [
                'Historical tours',
                'Museum visits',
                'Cultural workshops',
                'Traditional breakfast'
            ],
            'afternoon_activities': [
                'Cultural sites',
                'Art galleries',
                'Traditional crafts',
                'Religious sites'
            ],
            'evening_activities': [
                'Cultural performances',
                'Traditional dining',
                'Festival events',
                'Evening prayers/ceremonies'
            ]
        }
    }
    
    @staticmethod
    def detect_destination_type(destination):
        """
        Detect destination type based on destination name
        
        Args:
            destination (str): Destination name
            
        Returns:
            str: Detected destination type
        """
        destination_lower = destination.lower()
        
        # Beach destinations
        beach_keywords = ['beach', 'coast', 'island', 'seaside', 'ocean', 'bay', 'resort', 'riviera', 'maldives', 'bali', 'hawaii']
        if any(keyword in destination_lower for keyword in beach_keywords):
            return 'beach'
        
        # Mountain destinations
        mountain_keywords = ['mountain', 'hills', 'alps', 'peak', 'summit', 'valley', 'highland', 'himalayas', 'rockies', 'andes']
        if any(keyword in destination_lower for keyword in mountain_keywords):
            return 'mountain'
        
        # Cultural destinations
        cultural_keywords = ['temple', 'monastery', 'historic', 'ancient', 'heritage', 'unesco', 'cultural', 'traditional']
        if any(keyword in destination_lower for keyword in cultural_keywords):
            return 'cultural'
        
        # Default to city
        return 'city'
    
    @staticmethod
    def generate_default_itinerary(destination, start_date, end_date, destination_type=None):
        """
        Generate a default itinerary template
        
        Args:
            destination (str): Trip destination
            start_date (date): Trip start date
            end_date (date): Trip end date
            destination_type (str): Optional destination type override
            
        Returns:
            list: Generated itinerary template
        """
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Calculate trip duration
        duration = (end_date - start_date).days + 1
        
        # Auto-detect destination type if not provided
        if not destination_type:
            destination_type = ItineraryTemplate.detect_destination_type(destination)
        
        # Get activities for the detected type
        activities_data = ItineraryTemplate.DESTINATION_TYPES.get(destination_type, ItineraryTemplate.DESTINATION_TYPES['city'])
        
        itinerary = []
        current_date = start_date
        
        for day_num in range(1, duration + 1):
            day_itinerary = ItineraryTemplate._generate_day_itinerary(
                day_num, 
                current_date, 
                activities_data, 
                duration,
                destination
            )
            itinerary.append(day_itinerary)
            current_date += timedelta(days=1)
        
        return itinerary
    
    @staticmethod
    def _generate_day_itinerary(day_num, date, activities_data, total_days, destination):
        """
        Generate itinerary for a specific day
        
        Args:
            day_num (int): Day number
            date (date): Current date
            activities_data (dict): Activities data for destination type
            total_days (int): Total trip duration
            destination (str): Destination name
            
        Returns:
            dict: Day itinerary
        """
        day_itinerary = {
            'day': day_num,
            'date': date.strftime('%Y-%m-%d'),
            'day_of_week': date.strftime('%A'),
            'activities': []
        }
        
        # Special handling for first and last days
        if day_num == 1:
            day_itinerary['activities'] = ItineraryTemplate._get_arrival_day_activities(destination)
        elif day_num == total_days:
            day_itinerary['activities'] = ItineraryTemplate._get_departure_day_activities(destination)
        else:
            # Regular day activities
            morning_activity = ItineraryTemplate._select_activity(activities_data['morning_activities'])
            afternoon_activity = ItineraryTemplate._select_activity(activities_data['afternoon_activities'])
            evening_activity = ItineraryTemplate._select_activity(activities_data['evening_activities'])
            
            day_itinerary['activities'] = [
                {
                    'time': '09:00',
                    'activity': morning_activity,
                    'duration': '2-3 hours',
                    'type': 'morning'
                },
                {
                    'time': '13:00',
                    'activity': 'Lunch at local restaurant',
                    'duration': '1 hour',
                    'type': 'meal'
                },
                {
                    'time': '14:30',
                    'activity': afternoon_activity,
                    'duration': '3-4 hours',
                    'type': 'afternoon'
                },
                {
                    'time': '19:00',
                    'activity': evening_activity,
                    'duration': '2-3 hours',
                    'type': 'evening'
                }
            ]
        
        return day_itinerary
    
    @staticmethod
    def _get_arrival_day_activities(destination):
        """Generate activities for arrival day"""
        return [
            {
                'time': '10:00',
                'activity': f'Arrive in {destination}',
                'duration': '1 hour',
                'type': 'travel'
            },
            {
                'time': '11:00',
                'activity': 'Check into accommodation',
                'duration': '30 minutes',
                'type': 'accommodation'
            },
            {
                'time': '12:00',
                'activity': 'Welcome lunch at local restaurant',
                'duration': '1.5 hours',
                'type': 'meal'
            },
            {
                'time': '14:00',
                'activity': 'Orientation walk around neighborhood',
                'duration': '2 hours',
                'type': 'exploration'
            },
            {
                'time': '18:00',
                'activity': 'Relaxing dinner and early rest',
                'duration': '2 hours',
                'type': 'meal'
            }
        ]
    
    @staticmethod
    def _get_departure_day_activities(destination):
        """Generate activities for departure day"""
        return [
            {
                'time': '08:00',
                'activity': 'Final breakfast and packing',
                'duration': '1.5 hours',
                'type': 'meal'
            },
            {
                'time': '10:00',
                'activity': 'Last-minute souvenir shopping',
                'duration': '1.5 hours',
                'type': 'shopping'
            },
            {
                'time': '12:00',
                'activity': 'Check out of accommodation',
                'duration': '30 minutes',
                'type': 'accommodation'
            },
            {
                'time': '13:00',
                'activity': f'Departure from {destination}',
                'duration': '1 hour',
                'type': 'travel'
            }
        ]
    
    @staticmethod
    def _select_activity(activity_list):
        """Select a random activity from the list"""
        import random
        return random.choice(activity_list)
    
    @staticmethod
    def generate_custom_itinerary_template(trip_style='balanced', activity_level='moderate'):
        """
        Generate a customizable itinerary template
        
        Args:
            trip_style (str): Style of trip (relaxed, balanced, adventurous, cultural)
            activity_level (str): Activity level (low, moderate, high)
            
        Returns:
            dict: Itinerary template configuration
        """
        templates = {
            'relaxed': {
                'activities_per_day': 2,
                'pace': 'slow',
                'break_time': 'extended',
                'focus': ['relaxation', 'leisure', 'local_culture']
            },
            'balanced': {
                'activities_per_day': 3,
                'pace': 'moderate',
                'break_time': 'regular',
                'focus': ['sightseeing', 'culture', 'food', 'shopping']
            },
            'adventurous': {
                'activities_per_day': 4,
                'pace': 'fast',
                'break_time': 'minimal',
                'focus': ['adventure', 'sports', 'exploration', 'nightlife']
            },
            'cultural': {
                'activities_per_day': 3,
                'pace': 'moderate',
                'break_time': 'regular',
                'focus': ['museums', 'heritage', 'traditions', 'local_experiences']
            }
        }
        
        return templates.get(trip_style, templates['balanced'])
    
    @staticmethod
    def format_itinerary_for_storage(itinerary):
        """
        Format itinerary for database storage
        
        Args:
            itinerary (list): Itinerary data
            
        Returns:
            str: JSON formatted itinerary
        """
        return json.dumps(itinerary, indent=2, default=str)
    
    @staticmethod
    def parse_itinerary_from_storage(itinerary_json):
        """
        Parse itinerary from database storage
        
        Args:
            itinerary_json (str): JSON formatted itinerary
            
        Returns:
            list: Parsed itinerary data
        """
        if not itinerary_json:
            return []
        
        try:
            return json.loads(itinerary_json)
        except json.JSONDecodeError:
            return []
    
    @staticmethod
    def add_activity_to_day(itinerary, day_number, activity):
        """
        Add an activity to a specific day in the itinerary
        
        Args:
            itinerary (list): Current itinerary
            day_number (int): Day to add activity to
            activity (dict): Activity to add
            
        Returns:
            list: Updated itinerary
        """
        for day in itinerary:
            if day['day'] == day_number:
                day['activities'].append(activity)
                # Sort activities by time
                day['activities'].sort(key=lambda x: x.get('time', '00:00'))
                break
        
        return itinerary
    
    @staticmethod
    def remove_activity_from_day(itinerary, day_number, activity_index):
        """
        Remove an activity from a specific day
        
        Args:
            itinerary (list): Current itinerary
            day_number (int): Day to remove activity from
            activity_index (int): Index of activity to remove
            
        Returns:
            list: Updated itinerary
        """
        for day in itinerary:
            if day['day'] == day_number:
                if 0 <= activity_index < len(day['activities']):
                    day['activities'].pop(activity_index)
                break
        
        return itinerary
    
    @staticmethod
    def get_itinerary_summary(itinerary):
        """
        Get a summary of the itinerary
        
        Args:
            itinerary (list): Itinerary data
            
        Returns:
            dict: Itinerary summary
        """
        if not itinerary:
            return {'total_days': 0, 'total_activities': 0, 'activity_types': []}
        
        total_days = len(itinerary)
        total_activities = sum(len(day.get('activities', [])) for day in itinerary)
        
        activity_types = set()
        for day in itinerary:
            for activity in day.get('activities', []):
                activity_types.add(activity.get('type', 'general'))
        
        return {
            'total_days': total_days,
            'total_activities': total_activities,
            'activity_types': list(activity_types),
            'average_activities_per_day': round(total_activities / total_days, 1) if total_days > 0 else 0
        }
