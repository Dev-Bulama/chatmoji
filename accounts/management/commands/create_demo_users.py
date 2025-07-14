from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import FriendRequest, Friendship
from chat.models import Conversation, Message

User = get_user_model()

class Command(BaseCommand):
    help = 'Create demo users for testing ChatMoji'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing demo users before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing demo users...')
            User.objects.filter(email__in=[
                'john@example.com',
                'jane@example.com', 
                'mike@example.com',
                'sarah@example.com',
                'alex@example.com'
            ]).delete()

        # Demo users data
        demo_users = [
            {
                'email': 'john@example.com',
                'username': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'password': 'password123',
                'bio': 'Hey there! I love using ChatMoji to chat with friends. Every word becomes an emoji! 🚀',
                'is_online': True
            },
            {
                'email': 'jane@example.com',
                'username': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'password': 'password123',
                'bio': 'Software developer and emoji enthusiast. Always online and ready to chat! 💻',
                'is_online': True
            },
            {
                'email': 'mike@example.com',
                'username': 'mike@example.com',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'password': 'password123',
                'bio': 'Photographer and world traveler. Love connecting with people through ChatMoji! 📸',
                'is_online': False
            },
            {
                'email': 'sarah@example.com',
                'username': 'sarah@example.com',
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'password': 'password123',
                'bio': 'Teacher and lifelong learner. ChatMoji makes communication so much more fun! 📚',
                'is_online': True
            },
            {
                'email': 'alex@example.com',
                'username': 'alex@example.com',
                'first_name': 'Alex',
                'last_name': 'Brown',
                'password': 'password123',
                'bio': 'Musician and tech enthusiast. The emoji conversion feature is amazing! 🎵',
                'is_online': False
            }
        ]

        created_users = []
        
        # Create users
        for user_data in demo_users:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults=user_data
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {user.full_name} ({user.email})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'User already exists: {user.full_name} ({user.email})')
                )
            
            created_users.append(user)

        # Create friendships between some users
        friendships = [
            (0, 1),  # John & Jane
            (0, 3),  # John & Sarah
            (1, 2),  # Jane & Mike
            (1, 3),  # Jane & Sarah
            (2, 4),  # Mike & Alex
            (3, 4),  # Sarah & Alex
        ]

        for user1_idx, user2_idx in friendships:
            user1 = created_users[user1_idx]
            user2 = created_users[user2_idx]
            
            friendship, created = Friendship.objects.get_or_create(
                user1=user1,
                user2=user2
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created friendship: {user1.full_name} & {user2.full_name}')
                )

        # Create some pending friend requests
        if len(created_users) >= 5:
            pending_requests = [
                (0, 2),  # John -> Mike
                (4, 1),  # Alex -> Jane
            ]

            for from_idx, to_idx in pending_requests:
                from_user = created_users[from_idx]
                to_user = created_users[to_idx]
                
                request, created = FriendRequest.objects.get_or_create(
                    from_user=from_user,
                    to_user=to_user,
                    defaults={'status': 'pending'}
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created friend request: {from_user.full_name} -> {to_user.full_name}')
                    )

        # Create some demo conversations and messages
        if len(created_users) >= 2:
            # Create conversation between John and Jane
            john = created_users[0]
            jane = created_users[1]
            
            conversation, created = Conversation.objects.get_or_create(
                conversation_type='private',
                created_by=john,
                defaults={}
            )
            
            if created:
                conversation.participants.add(john, jane)
                
                # Create some demo messages
                demo_messages = [
                    {
                        'sender': john,
                        'content': 'Hello Jane! Welcome to ChatMoji!'
                    },
                    {
                        'sender': jane,
                        'content': 'Hi John! This emoji feature is amazing!'
                    },
                    {
                        'sender': john,
                        'content': 'I know right? Every word becomes an emoji!'
                    },
                    {
                        'sender': jane,
                        'content': 'Love it! This makes chatting so much more fun and expressive!'
                    }
                ]
                
                for msg_data in demo_messages:
                    Message.objects.create(
                        conversation=conversation,
                        sender=msg_data['sender'],
                        content=msg_data['content']
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created demo conversation with messages')
                )

        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Demo users created successfully!'))
        self.stdout.write('\nLogin credentials:')
        for user_data in demo_users:
            self.stdout.write(f"Email: {user_data['email']} | Password: {user_data['password']}")
        self.stdout.write('='*50)