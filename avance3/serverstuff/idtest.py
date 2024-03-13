import random

class UniqueObject:
    # Class variable to store existing IDs
    existing_ids = []

    def __init__(self, min_id=100, max_id=300):
        # Generate a unique ID upon object creation
        self.id = self.generate_unique_id(min_id, max_id)

    @classmethod
    def generate_unique_id(cls, min_id, max_id):
        """Generate a unique ID that's not already in existing_ids."""
        while True:
            new_id = random.randint(min_id, max_id)
            if new_id not in cls.existing_ids:
                # Add the new ID to the list of existing IDs
                cls.existing_ids.append(new_id)
                return new_id

# Create 100 UniqueObject instances and ensure no repeating IDs
objects = [UniqueObject(100, 999) for _ in range(100)]

# Optional: Print all IDs to verify uniqueness
for obj in objects:
    print(obj.id)
