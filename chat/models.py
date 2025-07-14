from django.db import models
from django.utils import timezone
from accounts.models import User
import uuid
import re
import logging

logger = logging.getLogger(__name__)

class Conversation(models.Model):
    CONVERSATION_TYPES = [
        ('private', 'Private'),
        ('group', 'Group'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    conversation_type = models.CharField(max_length=10, choices=CONVERSATION_TYPES, default='private')
    participants = models.ManyToManyField(User, related_name='conversations')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.name:
            return self.name
        if self.conversation_type == 'private':
            participants = list(self.participants.all())
            if len(participants) >= 2:
                return f"{participants[0]} & {participants[1]}"
        return f"Conversation {self.id}"
    
    @property
    def last_message(self):
        return self.messages.filter(is_deleted=False).order_by('-timestamp').first()
    
    def get_other_participant(self, user):
        """For private conversations, get the other participant"""
        if self.conversation_type == 'private':
            return self.participants.exclude(id=user.id).first()
        return None

class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    emoji_content = models.TextField(blank=True)  # Store emoji-converted version
    timestamp = models.DateTimeField(default=timezone.now)
    edited_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    # File attachments
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."

    def save(self, *args, **kwargs):
        # Convert emojis when saving
        if self.message_type == 'text' and self.content:
            try:
                if not self.emoji_content:  # Only convert if not already converted
                    self.emoji_content = self.convert_text_to_emojis(self.content)
            except Exception as e:
                logger.error(f"Error converting text to emojis: {e}")
                self.emoji_content = self.content  # Fallback to original
        
        # Update conversation timestamp
        is_new = not self.pk
        super().save(*args, **kwargs)
        
        if is_new:
            self.conversation.updated_at = self.timestamp
            self.conversation.save(update_fields=['updated_at'])
            
            # Just save the message - conversation update will be handled elsewhere
            super().save(*args, **kwargs)

    def convert_text_to_emojis(self, text):
        """Convert text to emojis using comprehensive mapping"""
        if not text or not text.strip():
            return text
        
        # Comprehensive emoji mapping
        emoji_map = {
            # === GREETINGS & SOCIAL ===
            'hello': '👋', 'hi': '👋', 'hey': '👋', 'greetings': '👋', 'howdy': '👋',
            'goodbye': '👋', 'bye': '👋', 'farewell': '👋', 'ciao': '👋', 'adieu': '👋',
            'welcome': '🤗', 'thanks': '🙏', 'thank': '🙏', 'please': '🙏', 
            'sorry': '😔', 'excuse': '🤷', 'pardon': '🤷', 'apologize': '😔',
            'good morning': '🌅', 'good night': '🌙', 'good evening': '🌆', 'good afternoon': '☀️',
            'congratulations': '🎉', 'congrats': '🎊', 'cheers': '🥂', 'toast': '🥂',
            'respect': '🙇', 'honor': '🎖️', 'bow': '🙇', 'salute': '🫡',

            # === EMOTIONS & FEELINGS ===
            'love': '❤️', 'heart': '❤️', 'adore': '😍', 'cherish': '💕', 'romance': '💕',
            'like': '👍', 'enjoy': '😊', 'appreciate': '👍', 'favor': '👍',
            'hate': '💔', 'despise': '😠', 'dislike': '👎', 'anger': '😡', 'mad': '😡',
            'happy': '😊', 'joy': '😁', 'excited': '🎉', 'celebrate': '🎊', 'party': '🎉',
            'sad': '😢', 'cry': '😭', 'tears': '😢', 'weep': '😭', 'sorrow': '😔',
            'laugh': '😂', 'lol': '😂', 'funny': '😂', 'hilarious': '🤣', 'joke': '😄',
            'smile': '😊', 'grin': '😁', 'beam': '😊', 'cheerful': '😊',
            'worried': '😟', 'anxious': '😰', 'nervous': '😬', 'stress': '😓',
            'surprise': '😲', 'shocked': '😱', 'amazed': '😮', 'wow': '😮',
            'confused': '😕', 'puzzled': '🤔', 'think': '🤔', 'wonder': '🤔',
            'tired': '😴', 'sleepy': '😴', 'exhausted': '😩', 'sleep': '😴',
            'angry': '😡', 'furious': '🤬', 'rage': '😠', 'annoyed': '😒',
            'embarrassed': '😳', 'shy': '😊', 'blush': '😊', 'modest': '😌',
            'proud': '😤', 'confident': '💪', 'brave': '🦁', 'courage': '🦸',
            'scared': '😨', 'afraid': '😰', 'fear': '😱', 'terrified': '😱',
            'calm': '😌', 'peaceful': '☮️', 'relaxed': '😌', 'zen': '🧘',
            'bored': '😑', 'meh': '😐', 'whatever': '🤷', 'indifferent': '😐',
            'jealous': '😒', 'envy': '💚', 'envious': '😤',
            'disgusted': '🤢', 'sick': '🤒', 'nauseous': '🤮', 'gross': '🤢',
            'relieved': '😅', 'phew': '😮‍💨', 'grateful': '🙏', 'blessed': '🙏',

            # === ACTIONS & ACTIVITIES ===
            'eat': '🍴', 'food': '🍽️', 'hungry': '🍽️', 'meal': '🍽️', 'dinner': '🍽️',
            'drink': '🥤', 'water': '💧', 'coffee': '☕', 'tea': '🍵', 'beer': '🍺',
            'work': '💼', 'job': '💼', 'office': '🏢', 'business': '💼', 'meeting': '🤝',
            'study': '📚', 'learn': '📖', 'school': '🏫', 'book': '📖', 'read': '📖',
            'travel': '✈️', 'trip': '🧳', 'vacation': '🏝️', 'journey': '🗺️', 'flight': '✈️',
            'music': '🎵', 'sing': '🎤', 'dance': '💃', 'song': '🎶', 'concert': '🎭',
            'movie': '🎬', 'film': '🎥', 'cinema': '🍿', 'watch': '👀', 'tv': '📺',
            'game': '🎮', 'play': '🎲', 'sport': '⚽', 'football': '⚽', 'basketball': '🏀',
            'cook': '👨‍🍳', 'recipe': '📝', 'kitchen': '🍳', 'bake': '🍰', 'chef': '👨‍🍳',
            'drive': '🚗', 'car': '🚗', 'bus': '🚌', 'train': '🚂', 'bike': '🚴',
            'walk': '🚶', 'run': '🏃', 'exercise': '🏋️', 'gym': '💪', 'fitness': '💪',
            'shop': '🛍️', 'buy': '💰', 'store': '🏪', 'market': '🛒', 'money': '💰',
            'phone': '📱', 'call': '📞', 'text': '💬', 'message': '💬', 'email': '📧',
            'clean': '🧽', 'wash': '🧼', 'shower': '🚿', 'bath': '🛁', 'brush': '🪥',
            'fix': '🔧', 'repair': '🛠️', 'build': '🔨', 'construct': '🏗️', 'create': '✨',
            'paint': '🎨', 'draw': '✏️', 'sketch': '📝', 'design': '🎨', 'art': '🖼️',
            'celebrate': '🎉', 'party': '🎊', 'dance': '💃', 'disco': '🕺',
            'relax': '🛋️', 'chill': '😎', 'rest': '🛌', 'nap': '😴',
            'meditate': '🧘', 'yoga': '🧘‍♀️', 'stretch': '🤸', 'breathe': '😤',
            'garden': '🌱', 'plant': '🌿', 'water': '💧', 'grow': '🌱',
            'climb': '🧗', 'hike': '🥾', 'camp': '⛺', 'fish': '🎣',
            'swim': '🏊', 'surf': '🏄', 'dive': '🤿', 'sail': '⛵',
            'knit': '🧶', 'sew': '🪡', 'craft': '✂️', 'hobby': '🎨',

            # === NATURE & WEATHER ===
            'sun': '☀️', 'sunny': '☀️', 'sunshine': '☀️', 'bright': '☀️', 'hot': '🔥',
            'rain': '🌧️', 'rainy': '🌧️', 'storm': '⛈️', 'thunder': '⛈️', 'wet': '💧',
            'snow': '❄️', 'snowy': '❄️', 'cold': '🥶', 'freeze': '🧊', 'winter': '❄️',
            'wind': '💨', 'windy': '💨', 'breeze': '🍃', 'air': '💨',
            'cloud': '☁️', 'cloudy': '☁️', 'sky': '🌌', 'star': '⭐', 'moon': '🌙',
            'flower': '🌸', 'tree': '🌳', 'grass': '🌱', 'nature': '🌿', 'garden': '🌻',
            'ocean': '🌊', 'sea': '🌊', 'water': '💧', 'beach': '🏖️', 'wave': '🌊',
            'mountain': '⛰️', 'hill': '🏔️', 'valley': '🏞️', 'forest': '🌲', 'jungle': '🌴',

            # === TIME & DATES ===
            'morning': '🌅', 'afternoon': '☀️', 'evening': '🌆', 'night': '🌙',
            'today': '📅', 'tomorrow': '📆', 'yesterday': '📋', 'week': '📅', 'month': '📅',
            'time': '⏰', 'clock': '🕐', 'hour': '⏰', 'minute': '⏱️', 'second': '⏱️',
            'birthday': '🎂', 'anniversary': '💒', 'holiday': '🏖️', 'christmas': '🎄',

            # === OBJECTS & THINGS ===
            'house': '🏠', 'home': '🏡', 'building': '🏢', 'city': '🏙️', 'town': '🏘️',
            'fire': '🔥', 'light': '💡', 'candle': '🕯️', 'lamp': '💡', 'electricity': '⚡',
            'computer': '💻', 'laptop': '💻', 'phone': '📱', 'internet': '🌐', 'wifi': '📶',
            'camera': '📷', 'photo': '📸', 'picture': '🖼️', 'art': '🎨', 'paint': '🎨',
            'pen': '✒️', 'pencil': '✏️', 'paper': '📄', 'notebook': '📓', 'write': '✍️',
            'key': '🔑', 'lock': '🔒', 'door': '🚪', 'window': '🪟', 'room': '🏠',
            'bed': '🛏️', 'pillow': '🛏️', 'blanket': '🛌', 'comfort': '🛌', 'rest': '😴',
            'chair': '🪑', 'table': '🪑', 'furniture': '🪑', 'sit': '🪑',

            # === ANIMALS ===
            'dog': '🐕', 'cat': '🐱', 'bird': '🐦', 'fish': '🐠', 'horse': '🐎',
            'cow': '🐄', 'pig': '🐷', 'sheep': '🐑', 'chicken': '🐔', 'duck': '🦆',
            'lion': '🦁', 'tiger': '🐅', 'bear': '🐻', 'wolf': '🐺', 'fox': '🦊',
            'rabbit': '🐰', 'mouse': '🐭', 'hamster': '🐹', 'pet': '🐾', 'zoo': '🦁',

            # === FOOD & DRINKS ===
            'pizza': '🍕', 'burger': '🍔', 'sandwich': '🥪', 'bread': '🍞', 'cheese': '🧀',
            'apple': '🍎', 'banana': '🍌', 'orange': '🍊', 'grape': '🍇', 'fruit': '🍎',
            'cake': '🍰', 'cookie': '🍪', 'chocolate': '🍫', 'candy': '🍬', 'sweet': '🍭',
            'ice': '🧊', 'cream': '🍦', 'dessert': '🍰', 'sugar': '🍯', 'honey': '🍯',
            'milk': '🥛', 'juice': '🧃', 'soda': '🥤', 'wine': '🍷', 'cocktail': '🍹',

            # === BODY PARTS ===
            'eye': '👁️', 'eyes': '👀', 'face': '😊', 'nose': '👃', 'mouth': '👄',
            'hand': '✋', 'finger': '👆', 'foot': '🦶', 'leg': '🦵', 'arm': '💪',
            'head': '🗣️', 'hair': '💇', 'ear': '👂', 'tooth': '🦷', 'heart': '❤️',

            # === COLORS ===
            'red': '🔴', 'blue': '🔵', 'green': '🟢', 'yellow': '🟡', 'orange': '🟠',
            'purple': '🟣', 'pink': '🩷', 'black': '⚫', 'white': '⚪', 'brown': '🤎',

            # === SYMBOLS & CONCEPTS ===
            'yes': '✅', 'no': '❌', 'ok': '👌', 'good': '👍', 'bad': '👎',
            'stop': '🛑', 'go': '🟢', 'wait': '⏳', 'hurry': '⏰', 'slow': '🐌',
            'fast': '⚡', 'quick': '⚡', 'speed': '💨', 'rush': '🏃',
            'help': '🆘', 'save': '💾', 'fix': '🔧', 'break': '💔', 'repair': '🔧',
            'new': '🆕', 'old': '🗝️', 'young': '👶', 'age': '👴', 'baby': '👶',
            'big': '📏', 'small': '🤏', 'large': '📏', 'tiny': '🤏', 'huge': '🦣',
            'near': '📍', 'far': '🔭', 'close': '🤝', 'distance': '📏', 'here': '📍',
            'up': '⬆️', 'down': '⬇️', 'left': '⬅️', 'right': '➡️', 'direction': '🧭',
            'important': '❗', 'urgent': '🚨', 'warning': '⚠️', 'danger': '☢️', 'safe': '🛡️',
            'secret': '🤫', 'private': '🔒', 'public': '📢', 'open': '🔓', 'closed': '🔒',
            'free': '🆓', 'cost': '💰', 'cheap': '💸', 'expensive': '💎', 'price': '💰',
            'win': '🏆', 'lose': '😞', 'victory': '🎊', 'defeat': '😔', 'compete': '🏁',
            'start': '▶️', 'finish': '🏁', 'end': '🔚', 'begin': '🆕', 'complete': '✅',
            'success': '🎯', 'fail': '❌', 'achievement': '🏆', 'goal': '🎯', 'dream': '💭',
            'idea': '💡', 'think': '🤔', 'brain': '🧠', 'smart': '🧠', 'genius': '🧠',
            'question': '❓', 'answer': '💡', 'problem': '❗', 'solution': '✅', 'help': '🆘',
            'friend': '👫', 'family': '👨‍👩‍👧‍👦', 'team': '👥', 'group': '👥', 'together': '🤝',
            'alone': '🧍', 'lonely': '😔', 'single': '1️⃣', 'couple': '👫', 'marriage': '💒',
            'peace': '☮️', 'war': '⚔️', 'fight': '👊', 'argue': '🗯️', 'agree': '🤝',
            'hope': '🌟', 'faith': '🙏', 'believe': '💫', 'trust': '🤝', 'doubt': '🤔',
            'chance': '🎰', 'luck': '🍀', 'fortune': '💰', 'random': '🎲', 'surprise': '🎁',
            'gift': '🎁', 'present': '🎁', 'reward': '🏆', 'prize': '🏅', 'medal': '🏅',
            'magic': '✨', 'spell': '🪄', 'wizard': '🧙', 'fairy': '🧚', 'fantasy': '🦄',
            'real': '💯', 'fake': '🎭', 'true': '✅', 'false': '❌', 'honest': '😇',
            'lie': '🤥', 'truth': '💯', 'fact': '📊', 'opinion': '💭', 'news': '📰',
            'information': 'ℹ️', 'data': '📊', 'knowledge': '🧠', 'wisdom': '🦉', 'learn': '📚',
            'teach': '👨‍🏫', 'student': '🎓', 'school': '🏫', 'university': '🏛️', 'education': '🎓',
            #=== TRANSPORTATION & VEHICLES ===
            'airplane': '✈️', 'helicopter': '🚁', 'rocket': '🚀', 'ship': '🚢', 'boat': '⛵',
            'motorcycle': '🏍️', 'scooter': '🛵', 'bicycle': '🚲', 'skateboard': '🛹',
            'truck': '🚛', 'van': '🚐', 'taxi': '🚕', 'police': '🚓', 'ambulance': '🚑',
            'fire truck': '🚒', 'tractor': '🚜', 'metro': '🚇', 'tram': '🚊',
            'traffic': '🚦', 'parking': '🅿️', 'gas': '⛽', 'fuel': '⛽',
            # === MEDICAL & HEALTH ===
            'doctor': '👨‍⚕️', 'nurse': '👩‍⚕️', 'hospital': '🏥', 'medicine': '💊', 'pill': '💊',
            'injection': '💉', 'bandage': '🩹', 'thermometer': '🌡️', 'stethoscope': '🩺',
            'health': '💪', 'healthy': '😊', 'sick': '🤒', 'fever': '🤒', 'virus': '🦠',
            'vaccine': '💉', 'surgery': '🏥', 'emergency': '🚨', 'first aid': '⛑️',
            'dental': '🦷', 'dentist': '🦷', 'glasses': '👓', 'contact': '👁️',
            'wheelchair': '♿', 'crutch': '🩼', 'prosthetic': '🦾',
            # === CLOTHING & ACCESSORIES ===
            'shirt': '👕', 'dress': '👗', 'pants': '👖', 'jeans': '👖', 'skirt': '👗',
            'jacket': '🧥', 'coat': '🧥', 'sweater': '🧶', 'hoodie': '🧥',
            'hat': '👒', 'cap': '🧢', 'helmet': '⛑️', 'crown': '👑',
            'shoes': '👟', 'boots': '🥾', 'heels': '👠', 'sandals': '👡',
            'socks': '🧦', 'gloves': '🧤', 'scarf': '🧣', 'tie': '👔',
            'jewelry': '💎', 'ring': '💍', 'necklace': '📿', 'watch': '⌚',
            'bag': '👜', 'backpack': '🎒', 'purse': '👛', 'wallet': '💳',
            'uniform': '👔', 'costume': '🎭', 'fashion': '👗',
            # === PROFESSIONS & JOBS ===
            'teacher': '👨‍🏫', 'student': '👨‍🎓', 'lawyer': '👨‍💼', 'judge': '👨‍⚖️',
            'police': '👮', 'firefighter': '👨‍🚒', 'pilot': '👨‍✈️', 'astronaut': '👨‍🚀',
            'chef': '👨‍🍳', 'waiter': '🧑‍🍳', 'farmer': '👨‍🌾', 'mechanic': '👨‍🔧',
            'scientist': '👨‍🔬', 'engineer': '👨‍💻', 'artist': '👨‍🎨', 'musician': '👨‍🎤',
            'actor': '🎭', 'director': '🎬', 'writer': '✍️', 'journalist': '📰',
            'photographer': '📸', 'designer': '🎨', 'architect': '🏗️',
            'carpenter': '🔨', 'plumber': '🔧', 'electrician': '⚡',
            # === SCIENCE & SPACE ===
            'space': '🌌', 'planet': '🪐', 'earth': '🌍', 'mars': '🔴', 'saturn': '🪐',
            'galaxy': '🌌', 'universe': '🌌', 'telescope': '🔭', 'satellite': '🛰️',
            'atom': '⚛️', 'molecule': '⚗️', 'chemistry': '🧪', 'physics': '⚛️',
            'biology': '🧬', 'dna': '🧬', 'microscope': '🔬', 'laboratory': '🧪',
            'experiment': '🧪', 'research': '🔬', 'discovery': '💡',
            'robot': '🤖', 'artificial': '🤖', 'technology': '💻',
            # === TOOLS & INSTRUMENTS ===
            'hammer': '🔨', 'screwdriver': '🪛', 'wrench': '🔧', 'saw': '🪚',
            'drill': '🪚', 'nail': '🔩', 'screw': '🔩', 'bolt': '🔩',
            'ladder': '🪜', 'rope': '🪢', 'chain': '⛓️', 'magnet': '🧲',
            'scale': '⚖️', 'ruler': '📏', 'compass': '🧭', 'calculator': '🧮',
            'scissors': '✂️', 'knife': '🔪', 'fork': '🍴', 'spoon': '🥄',
            'needle': '🪡', 'thread': '🧵', 'pin': '📌', 'clip': '📎',
            # === GEMS & JEWELRY ===
            'diamond': '💎', 'ruby': '♦️', 'emerald': '💚', 'sapphire': '💙',
            'pearl': '🤍', 'gold': '🥇', 'silver': '🥈', 'bronze': '🥉',
            'crystal': '💎', 'treasure': '💰', 'precious': '💎',
            # === SPORTS & FITNESS ===
            'soccer': '⚽', 'football': '🏈', 'basketball': '🏀', 'baseball': '⚾',
            'tennis': '🎾', 'golf': '⛳', 'hockey': '🏒', 'rugby': '🏉',
            'volleyball': '🏐', 'bowling': '🎳', 'boxing': '🥊', 'wrestling': '🤼',
            'swimming': '🏊', 'running': '🏃', 'cycling': '🚴', 'skiing': '⛷️',
            'surfing': '🏄', 'climbing': '🧗', 'gymnastics': '🤸', 'yoga': '🧘',
            'weightlifting': '🏋️', 'dumbbell': '🏋️', 'trophy': '🏆', 'medal': '🏅',
            'stadium': '🏟️', 'gym': '🏋️', 'pool': '🏊', 'track': '🏃',
            # === OFFICE & WORK ===
            'office': '🏢', 'desk': '🗄️', 'file': '📁', 'folder': '📂', 'document': '📄',
            'printer': '🖨️', 'fax': '📠', 'scanner': '🖨️', 'stapler': '📎',
            'briefcase': '💼', 'meeting': '🤝', 'presentation': '📊', 'chart': '📈',
            'deadline': '⏰', 'schedule': '📅', 'calendar': '📆', 'appointment': '📅',
            'salary': '💰', 'promotion': '📈', 'hire': '✅', 'fire': '❌',
            # === HOUSEHOLD ITEMS ===
            'sofa': '🛋️', 'couch': '🛋️', 'armchair': '🪑', 'desk': '🪑',
            'refrigerator': '❄️', 'microwave': '📱', 'oven': '🔥', 'stove': '🔥',
            'washing machine': '🌊', 'dryer': '💨', 'vacuum': '🧹', 'broom': '🧹',
            'toilet': '🚽', 'sink': '🚿', 'mirror': '🪞', 'towel': '🧻',
            'soap': '🧼', 'shampoo': '🧴', 'toothbrush': '🪥', 'comb': '💇',
            'iron': '🔥', 'hanger': '👔', 'basket': '🧺', 'trash': '🗑️',
            # === NUMBERS & MATH ===
            'zero': '0️⃣', 'one': '1️⃣', 'two': '2️⃣', 'three': '3️⃣', 'four': '4️⃣',
            'five': '5️⃣', 'six': '6️⃣', 'seven': '7️⃣', 'eight': '8️⃣', 'nine': '9️⃣',
            'ten': '🔟', 'hundred': '💯', 'thousand': '💯', 'million': '💰',
            'plus': '➕', 'minus': '➖', 'multiply': '✖️', 'divide': '➗',
            'equals': '🟰', 'percent': '💯', 'infinity': '♾️', 'math': '🔢',
            # === CELEBRATION & HOLIDAYS ===
            'christmas': '🎄', 'halloween': '🎃', 'easter': '🐰', 'valentine': '💝',
            'birthday': '🎂', 'anniversary': '💒', 'wedding': '👰', 'graduation': '🎓',
            'new year': '🎊', 'fireworks': '🎆', 'confetti': '🎊', 'balloon': '🎈',
            'candle': '🕯️', 'cake': '🎂', 'gift': '🎁', 'card': '💌',
            'party': '🎉', 'festival': '🎪', 'carnival': '🎠', 'parade': '🎭',
            # === PLANTS & FLOWERS ===
            'rose': '🌹', 'tulip': '🌷', 'sunflower': '🌻', 'daisy': '🌼',
            'lotus': '🪷', 'cherry': '🌸', 'blossom': '🌺', 'bouquet': '💐',
            'cactus': '🌵', 'palm': '🌴', 'bamboo': '🎋', 'fern': '🌿',
            'herb': '🌱', 'leaf': '🍃', 'branch': '🌿', 'root': '🌱',
            'seed': '🌰', 'fruit': '🍎', 'vegetable': '🥕', 'crop': '🌾',
            # === OFFICE ===
            'email': '📧', 'computer': '💻', 'keyboard': '⌨️', 'mouse': '🖱️',
            'conference': '🎤', 'zoom': '💻', 'call': '📞', 'phone': '📱',
            'report': '📋', 'spreadsheet': '📊', 'database': '🗃️',
            'project': '📋', 'task': '✅', 'todo': '📝', 'memo': '📝',
            'budget': '💰', 'invoice': '🧾', 'contract': '📜', 'signature': '✍️',
            'overtime': '⏰', 'break': '☕', 'lunch': '🍽️', 'vacation': '🏖️',
            #=== PRONOUNS ===
            # 'i': '👤', 'me': '👤', 'myself': '👤',
            # 'you': '👥', 'yourself': '👥', 'yourselves': '👥',
            # 'he': '👨', 'him': '👨', 'himself': '👨',
            # 'she': '👩', 'her': '👩', 'herself': '👩',
            # 'it': '📦', 'itself': '📦',
            # 'we': '👫', 'us': '👫', 'ourselves': '👫',
            # 'they': '👥', 'them': '👥', 'themselves': '👥',
            # 'my': '👤', 'mine': '👤',
            # 'your': '👥', 'yours': '👥',
            # 'his': '👨', 'hers': '👩', 'its': '📦',
            # 'our': '👫', 'ours': '👫',
            # 'their': '👥', 'theirs': '👥',
            # 'this': '👈', 'that': '👉', 'these': '👈', 'those': '👉',
            # 'here': '📍', 'there': '📍', 'everywhere': '🌐', 'somewhere': '🗺️',
            # 'who': '❓', 'whom': '❓', 'whose': '❓',
            # 'what': '❓', 'which': '❓',
            # 'where': '📍', 'when': '⏰', 'why': '❓', 'how': '❓',
            #=== ADJECTIVES ===
            'big': '📏', 'large': '📏', 'huge': '🦣', 'giant': '🦣', 'enormous': '🐘',
            'small': '🤏', 'little': '🤏', 'tiny': '🐜', 'mini': '🤏', 'microscopic': '🔬',
            'long': '📏', 'short': '📏', 'tall': '🦒', 'wide': '↔️', 'narrow': '🚪',
            'thick': '📖', 'thin': '📄', 'fat': '🐷', 'skinny': '🥖',
            'good': '👍', 'great': '🌟', 'excellent': '💯', 'perfect': '💯', 'amazing': '🤩',
            'bad': '👎', 'terrible': '💀', 'awful': '🤢', 'horrible': '😱', 'worst': '💩',
            'beautiful': '😍', 'pretty': '💖', 'gorgeous': '✨', 'stunning': '🤩',
            'ugly': '🙈', 'gross': '🤢', 'disgusting': '🤮',
            'clean': '✨', 'dirty': '🤢', 'messy': '🌪️', 'neat': '📐',
            'new': '🆕', 'old': '👴', 'fresh': '🌱', 'stale': '🥖', 'ancient': '🏛️',
            'broken': '💔', 'fixed': '🔧', 'damaged': '⚠️', 'perfect': '💯',
            'hot': '🔥', 'warm': '☀️', 'cool': '🌬️', 'cold': '🧊', 'freezing': '🥶',
            'dry': '🏜️', 'wet': '💧', 'humid': '💦', 'sunny': '☀️', 'cloudy': '☁️',
            'fast': '⚡', 'quick': '💨', 'rapid': '🏃', 'speedy': '🏎️',
            'slow': '🐌', 'gradual': '⏳', 'steady': '🚶',
            'easy': '😌', 'simple': '👌', 'difficult': '😤', 'hard': '💪', 'complex': '🧩',
            'impossible': '🚫', 'possible': '✅', 'probable': '🎯',
            #=== VERBS ===
            'run': '🏃', 'walk': '🚶', 'jump': '🦘', 'hop': '🐰', 'skip': '🦘',
            'sit': '🪑', 'stand': '🧍', 'lie': '🛌', 'sleep': '😴', 'wake': '⏰',
            'give': '🤲', 'take': '✋', 'bring': '📦', 'carry': '📦', 'hold': '✋',
            'push': '👐', 'pull': '🤝', 'lift': '🏋️', 'drop': '⬇️', 'throw': '🤾',
            'open': '🔓', 'close': '🔒', 'lock': '🔒', 'unlock': '🔑',
            'start': '▶️', 'stop': '⏹️', 'pause': '⏸️', 'continue': '▶️', 'finish': '🏁',
            'build': '🔨', 'break': '💥', 'fix': '🔧', 'destroy': '💥', 'create': '✨',
            'find': '🔍', 'lose': '❓', 'search': '🔍', 'discover': '💡', 'hide': '🙈',
            'buy': '💰', 'sell': '💸', 'pay': '💳', 'cost': '💰', 'spend': '💸',
            'win': '🏆', 'lose': '😞', 'compete': '🏁', 'play': '🎮', 'score': '⚽',
            'say': '💬', 'tell': '🗣️', 'speak': '🗣️', 'talk': '💬', 'whisper': '🤫',
            'shout': '📢', 'scream': '😱', 'yell': '📣', 'call': '📞',
            'ask': '❓', 'answer': '💡', 'reply': '↩️', 'respond': '💬',
            'listen': '👂', 'hear': '👂', 'read': '📖', 'write': '✍️', 'type': '⌨️',
            'think': '🤔', 'know': '🧠', 'understand': '💡', 'remember': '🧠', 'forget': '😵',
            'learn': '📚', 'study': '📖', 'teach': '👨‍🏫', 'explain': '💡',
            'believe': '💫', 'doubt': '🤔', 'trust': '🤝', 'hope': '🌟', 'wish': '⭐',
            'decide': '⚖️', 'choose': '👆', 'prefer': '👍', 'want': '🙏', 'need': '❗',
            #=== ADVERBS ===
            'quickly': '⚡', 'slowly': '🐌', 'carefully': '🔍', 'gently': '🤲',
            'loudly': '📢', 'quietly': '🤫', 'softly': '🤲', 'roughly': '💥',
            'easily': '😌', 'hardly': '😤', 'barely': '🤏', 'almost': '⏳',
            'suddenly': '⚡', 'gradually': '⏳', 'immediately': '⚡', 'eventually': '⏳',
            'clearly': '👁️', 'obviously': '💡', 'probably': '🤔', 'definitely': '💯',
            'now': '⏰', 'later': '⏳', 'soon': '⏰', 'early': '🌅', 'late': '🌙',
            'always': '♾️', 'never': '🚫', 'sometimes': '🎲', 'often': '🔄', 'rarely': '🤏',
            'today': '📅', 'yesterday': '📋', 'tomorrow': '📆',
            'before': '⏪', 'after': '⏩', 'during': '⏰', 'while': '⏰',
            'usually': '🔄', 'normally': '📊', 'typically': '📈', 'frequently': '🔄',
            'occasionally': '🎲', 'seldom': '🤏', 'hardly ever': '🚫',
            #=== PREPOSITIONS ===
            'in': '📦', 'on': '⬆️', 'at': '📍', 'by': '👥', 'near': '📍',
            'under': '⬇️', 'over': '⬆️', 'above': '☁️', 'below': '⬇️',
            'behind': '👈', 'in front': '👉', 'beside': '👥', 'between': '↔️',
            'inside': '📦', 'outside': '🌍', 'around': '🔄', 'through': '➡️',
            'across': '↔️', 'along': '➡️', 'against': '🚧', 'within': '📦',
            'to': '➡️', 'from': '⬅️', 'into': '📥', 'out of': '📤',
            'up': '⬆️', 'down': '⬇️', 'toward': '➡️', 'away': '⬅️',
            'off': '📤', 'onto': '📥', 'past': '➡️', 'beyond': '🔭',
            'before': '⏪', 'after': '⏩', 'during': '⏰', 'until': '⏳',
            'since': '📅', 'for': '⏰', 'within': '⏱️', 'throughout': '🔄',
            #=== CONJUNCTIONS ===
            'and': '➕', 'or': '❓', 'but': '⚖️', 'so': '➡️', 'yet': '⚖️',
            'nor': '🚫', 'for': '👉',
            'because': '👉', 'since': '📅', 'although': '⚖️', 'while': '⏰',
            'if': '❓', 'unless': '🚫', 'when': '⏰', 'where': '📍',
            'though': '⚖️', 'whereas': '⚖️', 'until': '⏳',
            #=== ARTICLES & DETERMINERS ===
            'a': '1️⃣', 'an': '1️⃣', 'the': '👆',
            'some': '🤏', 'any': '❓', 'many': '💯', 'few': '🤏', 'several': '👥',
            'all': '💯', 'every': '🔄', 'each': '👆', 'both': '2️⃣', 'either': '❓',
            'neither': '🚫', 'none': '0️⃣', 'no': '🚫',
            #=== INTERJECTIONS ===
            'wow': '😮', 'oh': '😮', 'ah': '😌', 'hey': '👋', 'hello': '👋',
            'oops': '😅', 'ouch': '😣', 'ugh': '😤', 'hmm': '🤔', 'shh': '🤫',
            'yay': '🎉', 'hooray': '🎊', 'bravo': '👏', 'alas': '😔',
            'duh': '🙄', 'meh': '😐', 'pfft': '💨', 'tsk': '😒',
            #=== MODAL VERBS ===
            'can': '💪', 'could': '🤔', 'may': '❓', 'might': '🤔', 'must': '❗',
            'should': '👍', 'would': '🤔', 'will': '➡️', 'shall': '➡️',
            'ought': '👍', 'need': '❗', 'dare': '🦁', 'used to': '📅',


        }
        
        # Convert text - case insensitive matching
        words = text.lower().split()
        converted_words = []
        
        for word in words:
            # Remove common punctuation for matching
            clean_word = re.sub(r'[.,!?;:]', '', word)
            
            # Check if word exists in emoji map
            if clean_word in emoji_map:
                # Keep original punctuation if it exists
                punctuation = word[len(clean_word):] if len(word) > len(clean_word) else ''
                converted_words.append(emoji_map[clean_word] + punctuation)
            else:
                converted_words.append(word)
        
        return ' '.join(converted_words)
        
    def get_fallback_emoji(self, word):
        """Get smart fallback emoji based on word characteristics"""
        if not word:
            return '✨'
        
        # Pattern-based fallbacks
        if re.search(r'[0-9]', word):
            return '🔢'
        
        # Ending-based fallbacks
        if word.endswith('ing'):
            return '⚡'
        elif word.endswith('ed'):
            return '✅'
        elif word.endswith('ly'):
            return '💫'
        elif word.endswith('er'):
            return '👤'
        elif word.endswith('est'):
            return '🏆'
        elif word.endswith('tion'):
            return '⚡'
        elif word.endswith('ness'):
            return '💫'
        elif word.endswith('ful'):
            return '🌈'
        elif word.endswith('less'):
            return '⭕'
        
        # Beginning-based fallbacks
        if word.startswith('un'):
            return '❌'
        elif word.startswith('pre'):
            return '⏪'
        elif word.startswith('pro'):
            return '👍'
        elif word.startswith('anti'):
            return '🚫'
        elif word.startswith('super'):
            return '⭐'
        elif word.startswith('mega'):
            return '🔥'
        elif word.startswith('micro') or word.startswith('mini'):
            return '🤏'
        
        # Length-based fallbacks
        length = len(word)
        if length == 1:
            return '👁️'
        elif length == 2:
            return '👀'
        elif length <= 4:
            return '💭'
        elif length <= 6:
            return '🌟'
        elif length <= 8:
            return '🎯'
        else:
            return '🚀'
    #@database_sync_to_async
    def save_message(self, content):
        try:
            from django.db import transaction
            
            with transaction.atomic():
                conversation = Conversation.objects.get(id=self.conversation_id)
                
                # Create and save message
                message = Message.objects.create(
                    conversation=conversation,
                    sender=self.user,
                    content=content,
                    message_type='text'
                )
                
                # Update conversation timestamp manually
                conversation.updated_at = message.timestamp
                conversation.save(update_fields=['updated_at'])
                
                return message
                
        except Conversation.DoesNotExist:
            logger.error(f"Conversation {self.conversation_id} does not exist")
            return None
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return None

class MessageRead(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, related_name='read_by', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='read_messages', on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user']
        ordering = ['-read_at']
    
    def __str__(self):
        return f"{self.user} read {self.message.id}"