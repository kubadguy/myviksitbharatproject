from faker import Faker
import hashlib

class FakeDataGenerator:
    def __init__(self):
        self.fake = Faker()

    def generate_users(self, count: int = 5):
        users = []
        for i in range(1, count + 1):
            users.append((
                i,
                self.fake.user_name(),
                self.fake.email(),
                hashlib.md5(self.fake.password().encode()).hexdigest(),
                round(self.fake.random.uniform(1000, 10000), 2)
            ))
        return users