/**
 * ChatMoji - Enhanced Emoji Converter
 * Converts text to emojis with advanced AI-like intelligence
 */

class EmojiConverter {
    constructor() {
        this.emojiMap = this.initializeEmojiMap();
        this.contextPatterns = this.initializeContextPatterns();
        this.fallbackEmojis = this.initializeFallbackEmojis();
        this.cache = new Map();
        this.stats = {
            conversions: 0,
            cacheHits: 0,
            totalWords: 0
        };
    }

    /**
     * Initialize comprehensive emoji mapping
     */
    initializeEmojiMap() {
        return {
            // === GREETINGS & SOCIAL ===
            'hello': '👋', 'hi': '👋', 'hey': '👋', 'greetings': '👋', 'howdy': '👋',
            'goodbye': '👋', 'bye': '👋', 'farewell': '👋', 'ciao': '👋', 'adieu': '👋',
            'welcome': '🤗', 'thanks': '🙏', 'thank': '🙏', 'please': '🙏', 
            'sorry': '😔', 'excuse': '🤷', 'pardon': '🤷', 'apologize': '😔',

            // === EMOTIONS & FEELINGS ===
            'love': '❤️', 'heart': '❤️', 'adore': '😍', 'cherish': '💕', 'romance': '💕',
            'like': '👍', 'enjoy': '😊', 'appreciate': '👍', 'favor': '👍',
            'hate': '💔', 'despise': '😤', 'loathe': '😡', 'detest': '💔',
            'angry': '😠', 'mad': '😡', 'furious': '🤬', 'rage': '😡', 'irritated': '😤',
            'happy': '😊', 'joy': '😄', 'joyful': '😄', 'cheerful': '😊', 'glad': '😊',
            'smile': '😊', 'grin': '😁', 'laugh': '😂', 'lol': '😂', 'haha': '😆',
            'giggle': '😆', 'chuckle': '😄', 'rofl': '🤣', 'lmao': '😂',
            'sad': '😢', 'cry': '😭', 'tears': '😭', 'weep': '😭', 'sob': '😭',
            'hurt': '💔', 'pain': '😣', 'ache': '😣', 'suffer': '😖',
            'sick': '🤒', 'ill': '🤒', 'unwell': '🤒', 'disease': '🦠',
            'excited': '🤩', 'thrilled': '🤩', 'ecstatic': '🤩', 'elated': '🤩',
            'amazing': '🤩', 'incredible': '🤩', 'fantastic': '🤩', 'wonderful': '🤩',
            'awesome': '🔥', 'cool': '😎', 'nice': '👌', 'great': '👍', 'excellent': '👌',
            'beautiful': '😍', 'pretty': '💅', 'gorgeous': '😍', 'stunning': '😍',
            'ugly': '🤮', 'hideous': '🤮', 'awful': '🤮',
            'scared': '😨', 'fear': '😰', 'afraid': '😰', 'terrified': '😱', 'panic': '😱',
            'tired': '😴', 'exhausted': '😴', 'sleepy': '😴', 'weary': '😴',
            'sleep': '😴', 'nap': '😴', 'rest': '😴', 'dream': '💭', 'nightmare': '😰',
            'wake': '⏰', 'awake': '👁️', 'alert': '👁️',
            'energy': '⚡', 'power': '⚡', 'strength': '💪', 'strong': '💪',
            'weak': '😵', 'faint': '😵', 'dizzy': '😵',
            'stress': '😩', 'pressure': '😩', 'tension': '😩', 'anxiety': '😰',
            'calm': '😌', 'peace': '☮️', 'peaceful': '😌', 'serene': '😌',
            'zen': '🧘', 'meditate': '🧘', 'relax': '😌', 'chill': '😎',

            // === ACTIONS & VERBS ===
            'go': '🚶', 'move': '🚶', 'walk': '🚶', 'stroll': '🚶', 'march': '🚶',
            'run': '🏃', 'sprint': '🏃', 'jog': '🏃', 'dash': '🏃', 'race': '🏃',
            'jump': '🦘', 'leap': '🦘', 'hop': '🦘', 'bounce': '🦘',
            'dance': '💃', 'dancing': '💃', 'groove': '💃', 'boogie': '💃',
            'sing': '🎤', 'singing': '🎤', 'song': '🎵', 'music': '🎵', 'melody': '🎵',
            'eat': '🍴', 'consume': '🍴', 'devour': '🍴', 'feast': '🍴', 'dine': '🍴',
            'drink': '🥤', 'sip': '🥤', 'gulp': '🥤', 'beverage': '🥤',
            'cook': '👨‍🍳', 'cooking': '👨‍🍳', 'prepare': '👨‍🍳', 'chef': '👨‍🍳',
            'read': '📖', 'reading': '📖', 'study': '📚', 'book': '📖', 'novel': '📖',
            'write': '✍️', 'writing': '✍️', 'author': '✍️', 'compose': '✍️',
            'draw': '🎨', 'drawing': '🎨', 'paint': '🎨', 'art': '🎨', 'sketch': '🎨',
            'play': '🎮', 'playing': '🎮', 'game': '🎮', 'gaming': '🎮', 'fun': '🎮',
            'watch': '👀', 'see': '👁️', 'look': '👀', 'observe': '👀', 'view': '👀',
            'listen': '👂', 'hear': '👂', 'sound': '🔊', 'audio': '🔊',
            'talk': '💬', 'speak': '🗣️', 'chat': '💬', 'conversation': '💬',
            'say': '💭', 'tell': '📢', 'announce': '📢', 'declare': '📢',
            'call': '📞', 'phone': '📞', 'ring': '📞', 'dial': '📞',
            'text': '📱', 'message': '💬', 'sms': '📱', 'email': '📧',
            'work': '💼', 'working': '💼', 'job': '💼', 'career': '💼', 'office': '🏢',
            'study': '📚', 'learn': '🎓', 'education': '🎓', 'school': '🏫',
            'teach': '👨‍🏫', 'teacher': '👨‍🏫', 'professor': '👨‍🏫', 'instructor': '👨‍🏫',
            'help': '🤝', 'assist': '🤝', 'support': '🤝', 'aid': '🤝',
            'buy': '💰', 'purchase': '💰', 'shop': '🛍️', 'shopping': '🛍️',
            'sell': '💸', 'pay': '💳', 'money': '💰', 'cash': '💵', 'dollar': '💵',
            'save': '💰', 'spend': '💸', 'cost': '💰', 'price': '💰',
            'drive': '🚗', 'driving': '🚗', 'car': '🚗', 'vehicle': '🚗',
            'travel': '✈️', 'trip': '✈️', 'journey': '✈️', 'vacation': '🏖️',
            'fly': '✈️', 'flight': '✈️', 'airplane': '✈️', 'plane': '✈️',
            'swim': '🏊', 'swimming': '🏊', 'pool': '🏊', 'water': '💧',
            'bike': '🚴', 'bicycle': '🚴', 'cycle': '🚴', 'cycling': '🚴',
            'boat': '⛵', 'ship': '🚢', 'sail': '⛵', 'sailing': '⛵',
            'build': '🔨', 'construction': '🔨', 'hammer': '🔨', 'tool': '🔨',
            'fix': '🔧', 'repair': '🔧', 'wrench': '🔧', 'mechanic': '🔧',
            'break': '💥', 'broken': '💥', 'smash': '💥', 'crash': '💥',
            'clean': '🧹', 'wash': '🧼', 'soap': '🧼', 'shower': '🚿',
            'dirty': '🧽', 'mess': '🧽', 'messy': '🧽',

            // === PEOPLE & RELATIONSHIPS ===
            'i': '👤', 'me': '👤', 'myself': '👤', 'self': '👤',
            'you': '👆', 'yourself': '👆', 'thou': '👆',
            'we': '👥', 'us': '👥', 'ourselves': '👥', 'together': '👥',
            'they': '👥', 'them': '👥', 'everyone': '👥', 'people': '👥',
            'family': '👨‍👩‍👧‍👦', 'relatives': '👨‍👩‍👧‍👦', 'kin': '👨‍👩‍👧‍👦',
            'mom': '👩', 'mother': '👩', 'mama': '👩', 'mommy': '👩',
            'dad': '👨', 'father': '👨', 'papa': '👨', 'daddy': '👨',
            'parents': '👨‍👩‍👧‍👦', 'parent': '👨‍👩‍👧‍👦',
            'baby': '👶', 'infant': '👶', 'newborn': '👶',
            'child': '🧒', 'kid': '🧒', 'children': '🧒', 'kids': '🧒',
            'teenager': '👦', 'teen': '👦', 'adolescent': '👦',
            'adult': '👤', 'grownup': '👤', 'mature': '👤',
            'friend': '👫', 'friends': '👥', 'buddy': '👫', 'pal': '👫',
            'friendship': '👫', 'companion': '👫', 'mate': '👫',
            'boyfriend': '👨‍❤️‍👨', 'girlfriend': '👩‍❤️‍👩', 'partner': '💑',
            'relationship': '💑', 'couple': '💑', 'romance': '💕',
            'wife': '👰', 'husband': '🤵', 'married': '💍', 'marriage': '💍',
            'wedding': '💒', 'bride': '👰', 'groom': '🤵',
            'brother': '👨', 'sister': '👩', 'sibling': '👫',
            'grandma': '👵', 'grandmother': '👵', 'granny': '👵',
            'grandpa': '👴', 'grandfather': '👴', 'grandparents': '👴',
            'uncle': '👨', 'aunt': '👩', 'cousin': '👫', 'nephew': '👦', 'niece': '👧',
            'teacher': '👨‍🏫', 'student': '👨‍🎓', 'pupil': '👨‍🎓',
            'doctor': '👨‍⚕️', 'nurse': '👩‍⚕️', 'hospital': '🏥', 'medical': '⚕️',
            'police': '👮', 'cop': '👮', 'officer': '👮', 'law': '⚖️',
            'boss': '👔', 'manager': '👔', 'employee': '👤', 'worker': '👷',
            'chef': '👨‍🍳', 'cook': '👨‍🍳', 'waiter': '🍽️', 'server': '🍽️',
            'pilot': '👨‍✈️', 'captain': '👨‍✈️', 'crew': '👥',
            'artist': '🎨', 'musician': '🎵', 'singer': '🎤', 'dancer': '💃',
            'actor': '🎭', 'actress': '🎭', 'performer': '🎭',
            'lawyer': '⚖️', 'judge': '⚖️', 'court': '⚖️',
            'scientist': '🔬', 'researcher': '🔬', 'laboratory': '🔬',
            'engineer': '⚙️', 'technician': '🔧', 'mechanic': '🔧',

            // === ANIMALS ===
            'cat': '🐱', 'kitten': '🐱', 'feline': '🐱', 'kitty': '🐱',
            'dog': '🐶', 'puppy': '🐶', 'canine': '🐶', 'hound': '🐶',
            'bird': '🐦', 'eagle': '🦅', 'owl': '🦉', 'penguin': '🐧',
            'chicken': '🐔', 'rooster': '🐓', 'duck': '🦆', 'goose': '🦆',
            'fish': '🐠', 'shark': '🦈', 'whale': '🐋', 'dolphin': '🐬',
            'octopus': '🐙', 'squid': '🦑', 'crab': '🦀', 'lobster': '🦞',
            'lion': '🦁', 'tiger': '🐅', 'leopard': '🐆', 'cheetah': '🐆',
            'elephant': '🐘', 'rhino': '🦏', 'hippo': '🦛', 'giraffe': '🦒',
            'monkey': '🐵', 'ape': '🦍', 'gorilla': '🦍', 'chimp': '🐵',
            'bear': '🐻', 'panda': '🐼', 'koala': '🐨', 'sloth': '🦥',
            'pig': '🐷', 'boar': '🐗', 'cow': '🐄', 'bull': '🐂',
            'horse': '🐴', 'pony': '🐴', 'zebra': '🦓', 'unicorn': '🦄',
            'rabbit': '🐰', 'bunny': '🐰', 'hare': '🐰',
            'mouse': '🐭', 'rat': '🐭', 'hamster': '🐹', 'squirrel': '🐿️',
            'snake': '🐍', 'lizard': '🦎', 'turtle': '🐢', 'frog': '🐸',
            'spider': '🕷️', 'ant': '🐜', 'bee': '🐝', 'butterfly': '🦋',
            'dragon': '🐉', 'dinosaur': '🦕', 'monster': '👹', 'alien': '👽',

            // === FOOD & DRINKS ===
            'food': '🍽️', 'meal': '🍽️', 'dinner': '🍽️', 'lunch': '🍽️', 'breakfast': '🍳',
            'hungry': '🤤', 'appetite': '🤤', 'starving': '🤤', 'famished': '🤤',
            'pizza': '🍕', 'slice': '🍕', 'pepperoni': '🍕', 'cheese': '🧀',
            'burger': '🍔', 'hamburger': '🍔', 'cheeseburger': '🍔',
            'fries': '🍟', 'chips': '🍟', 'french': '🍟', 'potato': '🥔',
            'pasta': '🍝', 'spaghetti': '🍝', 'noodles': '🍜', 'ramen': '🍜',
            'rice': '🍚', 'grain': '🌾', 'wheat': '🌾', 'bread': '🍞',
            'sandwich': '🥪', 'sub': '🥪', 'wrap': '🌯', 'burrito': '🌯',
            'taco': '🌮', 'nachos': '🌮', 'salsa': '🌮', 'mexican': '🌮',
            'meat': '🥩', 'beef': '🥩', 'steak': '🥩', 'pork': '🥓',
            'chicken': '🍗', 'poultry': '🍗', 'wing': '🍗', 'drumstick': '🍗',
            'fish': '🐟', 'salmon': '🐟', 'tuna': '🐟', 'seafood': '🦐',
            'egg': '🥚', 'omelet': '🍳', 'scrambled': '🍳', 'fried': '🍳',
            'milk': '🥛', 'dairy': '🥛', 'cream': '🥛', 'butter': '🧈',
            'coffee': '☕', 'espresso': '☕', 'cappuccino': '☕', 'latte': '☕',
            'tea': '🍵', 'green': '🍵', 'herbal': '🍵', 'chai': '🍵',
            'water': '💧', 'h2o': '💧', 'hydrate': '💧', 'thirsty': '💧',
            'juice': '🧃', 'smoothie': '🧃', 'shake': '🧃', 'drink': '🥤',
            'soda': '🥤', 'cola': '🥤', 'pop': '🥤', 'fizzy': '🥤',
            'beer': '🍺', 'ale': '🍺', 'lager': '🍺', 'brew': '🍺',
            'wine': '🍷', 'champagne': '🍾', 'alcohol': '🍷', 'cocktail': '🍸',
            'cake': '🎂', 'birthday': '🎂', 'candle': '🕯️', 'celebration': '🎉',
            'cookie': '🍪', 'biscuit': '🍪', 'cracker': '🍪', 'sweet': '🍭',
            'candy': '🍬', 'chocolate': '🍫', 'sugar': '🍭', 'dessert': '🍰',
            'ice': '🧊', 'cream': '🍦', 'frozen': '🧊', 'cold': '🧊',
            'apple': '🍎', 'red': '🍎', 'fruit': '🍎', 'healthy': '🍎',
            'banana': '🍌', 'yellow': '🍌', 'peel': '🍌', 'monkey': '🐵',
            'orange': '🍊', 'citrus': '🍊', 'vitamin': '🍊', 'juice': '🧃',
            'grape': '🍇', 'wine': '🍷', 'purple': '🍇', 'bunch': '🍇',
            'cherry': '🍒', 'berries': '🍒', 'strawberry': '🍓', 'blueberry': '🫐',
            'watermelon': '🍉', 'melon': '🍉', 'summer': '☀️', 'juicy': '🍉',
            'pineapple': '🍍', 'tropical': '🍍', 'hawaii': '🍍', 'sweet': '🍍',
            'coconut': '🥥', 'palm': '🌴', 'island': '🏝️', 'beach': '🏖️',
            'avocado': '🥑', 'green': '🥑', 'healthy': '🥑', 'toast': '🍞',
            'tomato': '🍅', 'vegetable': '🥕', 'salad': '🥗', 'fresh': '🥗',
            'carrot': '🥕', 'orange': '🥕', 'rabbit': '🐰', 'healthy': '🥕',
            'corn': '🌽', 'kernel': '🌽', 'yellow': '🌽', 'farm': '🚜',
            'pepper': '🌶️', 'spicy': '🌶️', 'hot': '🌶️', 'chili': '🌶️',
            'mushroom': '🍄', 'fungi': '🍄', 'forest': '🌲', 'pizza': '🍕',
            'garlic': '🧄', 'onion': '🧅', 'flavor': '🧄', 'cooking': '👨‍🍳',

            // === TECHNOLOGY & OBJECTS ===
            'phone': '📱', 'mobile': '📱', 'smartphone': '📱', 'iphone': '📱',
            'computer': '💻', 'laptop': '💻', 'pc': '💻', 'mac': '💻',
            'tablet': '📱', 'ipad': '📱', 'device': '📱', 'gadget': '📱',
            'internet': '🌐', 'web': '🌐', 'online': '🌐', 'website': '🌐',
            'wifi': '📶', 'signal': '📶', 'connection': '📶', 'network': '📶',
            'app': '📱', 'application': '📱', 'software': '💻', 'program': '💻',
            'email': '📧', 'message': '💬', 'text': '💬', 'chat': '💬',
            'photo': '📸', 'picture': '📸', 'image': '📸', 'selfie': '🤳',
            'camera': '📷', 'video': '📹', 'film': '📹', 'movie': '🎬',
            'music': '🎵', 'song': '🎶', 'tune': '🎵', 'melody': '🎵',
            'headphones': '🎧', 'speaker': '🔊', 'sound': '🔊', 'volume': '🔊',
            'tv': '📺', 'television': '📺', 'screen': '📺', 'monitor': '📺',
            'radio': '📻', 'podcast': '📻', 'broadcast': '📻', 'news': '📰',
            'car': '🚗', 'automobile': '🚗', 'vehicle': '🚗', 'drive': '🚗',
            'bus': '🚌', 'public': '🚌', 'transport': '🚌', 'commute': '🚌',
            'train': '🚊', 'subway': '🚇', 'rail': '🚊', 'locomotive': '🚂',
            'plane': '✈️', 'airplane': '✈️', 'flight': '✈️', 'airport': '✈️',
            'ship': '🚢', 'boat': '⛵', 'yacht': '🛥️', 'cruise': '🚢',
            'bike': '🚴', 'bicycle': '🚴', 'cycle': '🚴', 'pedal': '🚴',
            'motorcycle': '🏍️', 'scooter': '🛴', 'ride': '🏍️', 'biker': '🏍️',
            'house': '🏠', 'home': '🏡', 'building': '🏢', 'apartment': '🏢',
            'room': '🏠', 'bedroom': '🛏️', 'kitchen': '🍳', 'bathroom': '🚿',
            'door': '🚪', 'window': '🪟', 'roof': '🏠', 'wall': '🧱',
            'bed': '🛏️', 'sleep': '😴', 'pillow': '🛏️', 'blanket': '🛏️',
            'chair': '🪑', 'table': '🪑', 'desk': '🪑', 'furniture': '🪑',
            'couch': '🛋️', 'sofa': '🛋️', 'comfortable': '🛋️', 'relax': '🛋️',
            'lamp': '🪔', 'light': '💡', 'bulb': '💡', 'bright': '💡',
            'mirror': '🪞', 'reflection': '🪞', 'glass': '🪞', 'see': '👀',
            'clock': '⏰', 'time': '⏰', 'hour': '⏰', 'minute': '⏰',
            'calendar': '📅', 'date': '📅', 'schedule': '📅', 'appointment': '📅',
            'book': '📖', 'novel': '📖', 'read': '📖', 'story': '📖',
            'pen': '🖊️', 'pencil': '✏️', 'write': '✍️', 'draw': '✏️',
            'paper': '📄', 'document': '📄', 'file': '📄', 'page': '📄',
            'bag': '👜', 'purse': '👜', 'backpack': '🎒', 'luggage': '🧳',
            'clothes': '👕', 'clothing': '👕', 'wear': '👕', 'fashion': '👗',
            'shirt': '👕', 'blouse': '👕', 'top': '👕', 'tshirt': '👕',
            'pants': '👖', 'jeans': '👖', 'trousers': '👖', 'shorts': '🩳',
            'dress': '👗', 'skirt': '👗', 'gown': '👗', 'elegant': '👗',
            'shoes': '👟', 'sneakers': '👟', 'boots': '👢', 'sandals': '👡',
            'hat': '👒', 'cap': '🧢', 'helmet': '⛑️', 'crown': '👑',
            'glasses': '👓', 'sunglasses': '🕶️', 'vision': '👓', 'see': '👀',
            'watch': '⌚', 'timepiece': '⌚', 'clock': '⏰', 'time': '⏰',
            'jewelry': '💍', 'ring': '💍', 'necklace': '📿', 'bracelet': '📿',
            'money': '💰', 'cash': '💵', 'dollar': '💵', 'rich': '💰',
            'credit': '💳', 'card': '💳', 'payment': '💳', 'bank': '🏦',
            'gift': '🎁', 'present': '🎁', 'surprise': '🎁', 'birthday': '🎂',
            'key': '🔑', 'lock': '🔒', 'secure': '🔒', 'safe': '🔒',
            'tool': '🔨', 'hammer': '🔨', 'screwdriver': '🔧', 'wrench': '🔧',
            'scissors': '✂️', 'cut': '✂️', 'sharp': '✂️', 'blade': '🔪',
            'knife': '🔪', 'fork': '🍴', 'spoon': '🥄', 'plate': '🍽️',
            'cup': '☕', 'mug': '☕', 'glass': '🥃', 'bottle': '🍼',
            'umbrella': '☂️', 'rain': '🌧️', 'weather': '🌤️', 'protection': '☂️',
            'fire': '🔥', 'flame': '🔥', 'hot': '🔥', 'burn': '🔥',
            'candle': '🕯️', 'light': '💡', 'wax': '🕯️', 'romantic': '💕',
            'battery': '🔋', 'power': '⚡', 'energy': '⚡', 'charge': '🔋',
            'magnet': '🧲', 'attract': '🧲', 'magnetic': '🧲', 'pull': '🧲',

            // === PLACES & LOCATIONS ===
            'world': '🌍', 'earth': '🌍', 'globe': '🌍', 'planet': '🌍',
            'country': '🏞️', 'nation': '🏞️', 'land': '🏞️', 'territory': '🏞️',
            'city': '🏙️', 'town': '🏘️', 'village': '🏘️', 'urban': '🏙️',
            'street': '🛣️', 'road': '🛣️', 'avenue': '🛣️', 'highway': '🛣️',
            'school': '🏫', 'university': '🏫', 'college': '🏫', 'education': '🎓',
            'hospital': '🏥', 'clinic': '🏥', 'medical': '⚕️', 'doctor': '👨‍⚕️',
            'store': '🏪', 'shop': '🏪', 'market': '🏪', 'mall': '🏪',
            'restaurant': '🍽️', 'cafe': '☕', 'diner': '🍽️', 'bistro': '🍽️',
            'park': '🏞️', 'garden': '🌻', 'playground': '🛝', 'nature': '🌿',
            'beach': '🏖️', 'ocean': '🌊', 'sea': '🌊', 'sand': '🏖️',
            'mountain': '⛰️', 'hill': '⛰️', 'peak': '⛰️', 'climb': '🧗',
            'forest': '🌲', 'woods': '🌲', 'trees': '🌳', 'jungle': '🌿',
            'desert': '🏜️', 'sand': '🏜️', 'hot': '🔥', 'dry': '🏜️',
            'river': '🌊', 'stream': '🌊', 'lake': '🌊', 'pond': '🌊',
            'bridge': '🌉', 'tunnel': '🌉', 'cross': '🌉', 'connect': '🔗',
            'airport': '✈️', 'station': '🚉', 'terminal': '🚉', 'platform': '🚉',
            'office': '🏢', 'workplace': '🏢', 'business': '💼', 'corporate': '🏢',
            'bank': '🏦', 'atm': '🏦', 'money': '💰', 'finance': '💰',
            'church': '⛪', 'temple': '🏛️', 'mosque': '🕌', 'synagogue': '🕍',
            'library': '📚', 'books': '📚', 'quiet': '🤫', 'study': '📚',
            'gym': '🏋️', 'fitness': '🏋️', 'workout': '🏋️', 'exercise': '🏋️',
            'pool': '🏊', 'swimming': '🏊', 'water': '💧', 'swim': '🏊',
            'stadium': '🏟️', 'arena': '🏟️', 'sports': '⚽', 'game': '🎮',
            'theater': '🎭', 'cinema': '🎬', 'movie': '🎬', 'film': '🎬',
            'museum': '🏛️', 'art': '🎨', 'history': '🏛️', 'culture': '🎨',
            'zoo': '🦁', 'animals': '🦁', 'wildlife': '🦁', 'safari': '🦁',
            'farm': '🚜', 'ranch': '🚜', 'agriculture': '🚜', 'crops': '🌾',
            'factory': '🏭', 'industry': '🏭', 'manufacturing': '🏭', 'production': '🏭',
            'castle': '🏰', 'palace': '🏰', 'fortress': '🏰', 'royal': '👑',
            'tower': '🗼', 'skyscraper': '🏢', 'tall': '🗼', 'high': '🗼',
            'lighthouse': '🗼', 'beacon': '🗼', 'guide': '🗼', 'ships': '⛵',
            'tent': '⛺', 'camping': '⛺', 'outdoor': '⛺', 'adventure': '⛺',
            'cabin': '🏠', 'cottage': '🏠', 'hut': '🏠', 'lodge': '🏠',

            // === TIME & WEATHER ===
            'time': '⏰', 'clock': '⏰', 'hour': '⏰', 'minute': '⏰',
            'second': '⏰', 'moment': '⏰', 'instant': '⏰', 'now': '⏰',
            'day': '☀️', 'today': '📅', 'daily': '📅', 'date': '📅',
            'night': '🌙', 'evening': '🌆', 'midnight': '🌙', 'dark': '🌙',
            'morning': '🌅', 'dawn': '🌅', 'sunrise': '🌅', 'early': '🌅',
            'afternoon': '☀️', 'noon': '☀️', 'midday': '☀️', 'lunch': '🍽️',
            'sunset': '🌇', 'dusk': '🌇', 'twilight': '🌇', 'golden': '🌇',
            'tomorrow': '📅', 'future': '📅', 'next': '📅', 'upcoming': '📅',
            'yesterday': '📅', 'past': '📅', 'previous': '📅', 'ago': '📅',
            'week': '📅', 'weekly': '📅', 'weekend': '📅', 'weekday': '📅',
            'month': '📅', 'monthly': '📅', 'year': '📅', 'yearly': '📅',
            'season': '🍂', 'spring': '🌸', 'summer': '☀️', 'autumn': '🍂',
            'winter': '❄️', 'fall': '🍂', 'seasonal': '🍂', 'change': '🍂',
            'weather': '🌤️', 'forecast': '🌤️', 'climate': '🌤️', 'temperature': '🌡️',
            'sun': '☀️', 'sunny': '☀️', 'sunshine': '☀️', 'bright': '☀️',
            'rain': '🌧️', 'rainy': '🌧️', 'drizzle': '🌧️', 'shower': '🌧️',
            'snow': '❄️', 'snowy': '❄️', 'blizzard': '❄️', 'winter': '❄️',
            'wind': '💨', 'windy': '💨', 'breeze': '💨', 'gust': '💨',
            'storm': '⛈️', 'thunder': '⛈️', 'lightning': '⛈️', 'tempest': '⛈️',
            'cloud': '☁️', 'cloudy': '☁️', 'overcast': '☁️', 'gray': '☁️',
            'fog': '🌫️', 'mist': '🌫️', 'haze': '🌫️', 'foggy': '🌫️',
            'hot': '🔥', 'heat': '🔥', 'warm': '☀️', 'temperature': '🌡️',
            'cold': '🥶', 'freezing': '🥶', 'ice': '🧊', 'frost': '❄️',
            'cool': '❄️', 'chilly': '🥶', 'crisp': '❄️', 'fresh': '❄️',
            'humid': '💧', 'humidity': '💧', 'moist': '💧', 'damp': '💧',
            'dry': '🏜️', 'drought': '🏜️', 'arid': '🏜️', 'parched': '🏜️',

            // === COLORS ===
            'red': '🔴', 'crimson': '🔴', 'scarlet': '🔴', 'ruby': '🔴',
            'blue': '🔵', 'azure': '🔵', 'navy': '🔵', 'cobalt': '🔵',
            'green': '🟢', 'emerald': '🟢', 'lime': '🟢', 'olive': '🟢',
            'yellow': '🟡', 'gold': '🟡', 'amber': '🟡', 'lemon': '🟡',
            'orange': '🟠', 'tangerine': '🟠', 'peach': '🟠', 'coral': '🟠',
            'purple': '🟣', 'violet': '🟣', 'lavender': '🟣', 'plum': '🟣',
            'pink': '💗', 'rose': '💗', 'magenta': '💗', 'fuchsia': '💗',
            'brown': '🤎', 'tan': '🤎', 'bronze': '🤎', 'chocolate': '🤎',
            'black': '⚫', 'dark': '⚫', 'ebony': '⚫', 'coal': '⚫',
            'white': '⚪', 'ivory': '⚪', 'pearl': '⚪', 'snow': '❄️',
            'gray': '⚪', 'grey': '⚪', 'silver': '⚪', 'ash': '⚪',
            'rainbow': '🌈', 'colorful': '🌈', 'spectrum': '🌈', 'prism': '🌈',

            // === NUMBERS & QUANTITIES ===
            'zero': '0️⃣', 'nothing': '0️⃣', 'empty': '0️⃣', 'none': '0️⃣',
            'one': '1️⃣', 'single': '1️⃣', 'alone': '1️⃣', 'solo': '1️⃣',
            'two': '2️⃣', 'pair': '2️⃣', 'double': '2️⃣', 'couple': '2️⃣',
            'three': '3️⃣', 'triple': '3️⃣', 'trio': '3️⃣', 'third': '3️⃣',
            'four': '4️⃣', 'quad': '4️⃣', 'quarter': '4️⃣', 'fourth': '4️⃣',
            'five': '5️⃣', 'fifth': '5️⃣', 'quint': '5️⃣', 'hand': '✋',
            'six': '6️⃣', 'sixth': '6️⃣', 'half': '6️⃣', 'dozen': '6️⃣',
            'seven': '7️⃣', 'seventh': '7️⃣', 'lucky': '7️⃣', 'week': '7️⃣',
            'eight': '8️⃣', 'eighth': '8️⃣', 'octo': '8️⃣', 'infinity': '♾️',
            'nine': '9️⃣', 'ninth': '9️⃣', 'cloud': '☁️', 'almost': '9️⃣',
            'ten': '🔟', 'tenth': '🔟', 'decimal': '🔟', 'perfect': '🔟',
            'eleven': '🔟', 'twelve': '🔟', 'dozen': '🔟', 'thirteen': '🔟',
            'twenty': '🔟', 'thirty': '🔟', 'forty': '🔟', 'fifty': '🔟',
            'hundred': '💯', 'thousand': '💯', 'million': '💰', 'billion': '💰',
            'many': '💯', 'lots': '💯', 'numerous': '💯', 'multiple': '💯',
            'few': '✌️', 'several': '✌️', 'some': '👌', 'little': '🤏',
            'all': '💯', 'everything': '💯', 'total': '💯', 'complete': '💯',
            'big': '🔢', 'large': '📏', 'huge': '🦣', 'giant': '🦣',
            'small': '🤏', 'tiny': '🐭', 'mini': '🤏', 'micro': '🤏',
            'long': '📏', 'short': '🤏', 'tall': '🗼', 'high': '🗼',
            'wide': '📏', 'narrow': '🤏', 'thick': '📏', 'thin': '🤏',
            'heavy': '🏋️', 'light': '🪶', 'weight': '🏋️', 'mass': '🏋️',

            // === STATES & CONDITIONS ===
            'new': '✨', 'fresh': '✨', 'novel': '✨', 'recent': '✨',
            'old': '👴', 'ancient': '👴', 'vintage': '👴', 'antique': '👴',
            'young': '👶', 'youthful': '👶', 'juvenile': '👶', 'immature': '👶',
            'fast': '💨', 'quick': '⚡', 'rapid': '💨', 'swift': '💨',
            'slow': '🐌', 'sluggish': '🐌', 'gradual': '🐌', 'steady': '🐌',
            'strong': '💪', 'powerful': '💪', 'mighty': '💪', 'robust': '💪',
            'weak': '😵', 'feeble': '😵', 'fragile': '😵', 'delicate': '😵',
            'easy': '👌', 'simple': '👌', 'effortless': '👌', 'basic': '👌',
            'hard': '💪', 'difficult': '😤', 'challenging': '😤', 'tough': '💪',
            'soft': '🪶', 'gentle': '🪶', 'tender': '🪶', 'smooth': '🪶',
            'rough': '🪨', 'coarse': '🪨', 'bumpy': '🪨', 'jagged': '🪨',
            'sharp': '⚡', 'pointed': '⚡', 'keen': '⚡', 'cutting': '✂️',
            'dull': '😴', 'blunt': '😴', 'boring': '😴', 'tedious': '😴',
            'bright': '💡', 'brilliant': '💡', 'shiny': '✨', 'glowing': '✨',
            'dark': '🌙', 'dim': '🌙', 'shadowy': '🌙', 'gloomy': '🌙',
            'clean': '🧹', 'pure': '🧹', 'spotless': '🧹', 'pristine': '🧹',
            'dirty': '🧽', 'messy': '🧽', 'filthy': '🧽', 'grimy': '🧽',
            'full': '🌕', 'complete': '💯', 'filled': '🌕', 'packed': '🌕',
            'empty': '⭕', 'vacant': '⭕', 'hollow': '⭕', 'void': '⭕',
            'open': '🔓', 'unlocked': '🔓', 'accessible': '🔓', 'available': '🔓',
            'closed': '🔒', 'locked': '🔒', 'sealed': '🔒', 'shut': '🔒',
            'right': '✅', 'correct': '✅', 'accurate': '✅', 'proper': '✅',
            'wrong': '❌', 'incorrect': '❌', 'false': '❌', 'mistaken': '❌',
            'true': '✅', 'real': '✅', 'genuine': '✅', 'authentic': '✅',
            'fake': '❌', 'false': '❌', 'artificial': '❌', 'counterfeit': '❌',
            'good': '👍', 'great': '👍', 'excellent': '👌', 'perfect': '💯',
            'bad': '👎', 'terrible': '👎', 'awful': '👎', 'horrible': '👎',
            'best': '🏆', 'top': '🏆', 'finest': '🏆', 'supreme': '🏆',
            'worst': '👎', 'bottom': '👎', 'lowest': '👎', 'poorest': '👎',
            'better': '👍', 'improved': '📈', 'superior': '👍', 'enhanced': '📈',
            'worse': '👎', 'inferior': '👎', 'degraded': '👎', 'declined': '👎',
            'safe': '🔒', 'secure': '🔒', 'protected': '🔒', 'guarded': '🔒',
            'dangerous': '⚠️', 'risky': '⚠️', 'hazardous': '⚠️', 'unsafe': '⚠️',
            'healthy': '🍎', 'fit': '🏋️', 'well': '🍎', 'robust': '💪',
            'sick': '🤒', 'ill': '🤒', 'unwell': '🤒', 'diseased': '🦠',
            'alive': '💚', 'living': '💚', 'breathing': '💚', 'vital': '💚',
            'dead': '💀', 'deceased': '💀', 'lifeless': '💀', 'extinct': '💀',
            'active': '⚡', 'busy': '⚡', 'dynamic': '⚡', 'energetic': '⚡',
            'inactive': '😴', 'idle': '😴', 'passive': '😴', 'dormant': '😴',
            'awake': '👁️', 'alert': '👁️', 'conscious': '👁️', 'aware': '👁️',
            'asleep': '😴', 'sleeping': '😴', 'unconscious': '😴', 'dreaming': '💭',

            // === RESPONSES & EXPRESSIONS ===
            'yes': '✅', 'yeah': '✅', 'yep': '✅', 'affirmative': '✅',
            'no': '❌', 'nope': '❌', 'negative': '❌', 'never': '❌',
            'maybe': '🤷', 'perhaps': '🤷', 'possibly': '🤷', 'uncertain': '🤷',
            'ok': '👌', 'okay': '👌', 'alright': '👌', 'fine': '👌',
            'sure': '👍', 'certainly': '👍', 'definitely': '💯', 'absolutely': '💯',
            'wow': '😮', 'whoa': '😮', 'amazing': '🤩', 'incredible': '🤩',
            'omg': '😱', 'gosh': '😱', 'goodness': '😱', 'mercy': '😱',
            'really': '😲', 'seriously': '😐', 'truly': '😲', 'honestly': '😲',
            'exactly': '💯', 'precisely': '💯', 'totally': '💯', 'completely': '💯',
            'always': '💯', 'forever': '💯', 'constantly': '💯', 'continually': '💯',
            'never': '❌', 'not': '❌', 'none': '❌', 'zero': '0️⃣',
            'sometimes': '🤷', 'occasionally': '🤷', 'rarely': '🤏', 'seldom': '🤏',
            'often': '🔄', 'frequently': '🔄', 'usually': '🔄', 'commonly': '🔄',
            'hmm': '🤔', 'thinking': '🤔', 'wondering': '🤔', 'pondering': '🤔',
            'oh': '😮', 'ah': '😮', 'eh': '🤷', 'um': '🤔',
            'huh': '🤔', 'what': '❓', 'why': '❓', 'how': '🤔',
            'when': '⏰', 'where': '📍', 'who': '👤', 'which': '🤔',
            'oops': '😅', 'ouch': '😣', 'yikes': '😬', 'whoops': '😅',
            'phew': '😅', 'relief': '😅', 'sigh': '😔', 'breathe': '😤',
            'tada': '🎉', 'hooray': '🎉', 'yay': '🎉', 'celebrate': '🎉',
            'congratulations': '🎉', 'congrats': '🎉', 'bravo': '👏', 'applause': '👏',
            'shh': '🤫', 'quiet': '🤫', 'silence': '🤫', 'hush': '🤫',
            'help': '🆘', 'emergency': '🆘', 'urgent': '🆘', 'crisis': '🆘',
            'stop': '⏹️', 'halt': '⏹️', 'wait': '⏸️', 'pause': '⏸️',
            'go': '▶️', 'start': '▶️', 'begin': '▶️', 'commence': '▶️',
            'end': '🔚', 'finish': '✅', 'complete': '✅', 'done': '✅',
            'continue': '▶️', 'proceed': '▶️', 'advance': '▶️', 'progress': '📈',
            'back': '⬅️', 'return': '⬅️', 'backward': '⬅️', 'reverse': '⬅️',
            'forward': '➡️', 'ahead': '➡️', 'onward': '➡️', 'next': '⏭️',
            'up': '⬆️', 'above': '⬆️', 'higher': '⬆️', 'upward': '⬆️',
            'down': '⬇️', 'below': '⬇️', 'lower': '⬇️', 'downward': '⬇️',
            'left': '⬅️', 'right': '➡️', 'straight': '⬆️', 'diagonal': '↗️',
            'in': '📥', 'inside': '📥', 'within': '📥', 'interior': '📥',
            'out': '📤', 'outside': '📤', 'exterior': '📤', 'beyond': '📤',
            'on': '🔛', 'off': '📴', 'over': '⬆️', 'under': '⬇️',
            'around': '🔄', 'through': '➡️', 'across': '↔️', 'between': '↔️',
            'among': '👥', 'within': '📥', 'near': '📍', 'far': '🔭',
            'close': '🤏', 'distant': '🔭', 'away': '👋', 'apart': '↔️',
            'together': '👥', 'united': '👥', 'joined': '🔗', 'connected': '🔗',
            'separated': '↔️', 'divided': '↔️', 'split': '↔️', 'broken': '💔',
            'with': '🤝', 'without': '❌', 'plus': '➕', 'minus': '➖',
            'and': '➕', 'or': '🤷', 'but': '🤷', 'so': '💭',
            'if': '🤔', 'then': '👉', 'else': '🤷', 'because': '💭',
            'very': '💯', 'extremely': '💯', 'quite': '💯', 'really': '💯',
            'too': '➕', 'also': '➕', 'additionally': '➕', 'furthermore': '➕',
            'just': '👌', 'only': '☝️', 'merely': '☝️', 'simply': '👌',
            'still': '⏳', 'yet': '⏳', 'already': '✅', 'soon': '⏳',
            'first': '1️⃣', 'second': '2️⃣', 'third': '3️⃣', 'last': '🔚',
            'final': '🔚', 'ultimate': '🔚', 'beginning': '▶️', 'middle': '⏯️',
            'important': '❗', 'urgent': '🆘', 'critical': '❗', 'vital': '❗',
            'special': '⭐', 'unique': '⭐', 'rare': '⭐', 'precious': '💎',
            'common': '👥', 'ordinary': '👥', 'normal': '👥', 'regular': '👥',
            'different': '🆚', 'same': '🟰', 'similar': '🟰', 'alike': '🟰',
            'opposite': '🆚', 'contrary': '🆚', 'reverse': '🔄', 'inverse': '🔄',
        };
    }

    /**
     * Initialize context patterns for better emoji selection
     */
    initializeContextPatterns() {
        return {
            technology: ['app', 'computer', 'phone', 'internet', 'software', 'digital'],
            emotions: ['happy', 'sad', 'angry', 'excited', 'scared', 'love'],
            nature: ['tree', 'flower', 'sun', 'moon', 'water', 'mountain'],
            food: ['eat', 'drink', 'cook', 'hungry', 'delicious', 'taste'],
            time: ['day', 'night', 'morning', 'evening', 'time', 'clock'],
            weather: ['sun', 'rain', 'snow', 'wind', 'storm', 'cloud'],
            animals: ['cat', 'dog', 'bird', 'fish', 'lion', 'elephant'],
            actions: ['run', 'walk', 'jump', 'dance', 'sing', 'play'],
            people: ['family', 'friend', 'mom', 'dad', 'baby', 'teacher'],
            places: ['home', 'school', 'park', 'beach', 'city', 'country']
        };
    }

    /**
     * Initialize fallback emojis based on word characteristics
     */
    initializeFallbackEmojis() {
        return {
            length: {
                1: '👁️',
                2: '👀',
                3: '💭',
                4: '🌟',
                5: '🎯',
                6: '🚀',
                7: '⚡',
                8: '🔥',
                9: '💎',
                10: '🌈'
            },
            endings: {
                'ing': '⚡',
                'ed': '✅',
                'ly': '💫',
                'er': '👤',
                'est': '🏆',
                'tion': '⚡',
                'ness': '💫',
                'ful': '🌈',
                'less': '⭕',
                'ment': '📋',
                'able': '👌',
                'ible': '👌'
            },
            beginnings: {
                'un': '❌',
                'pre': '⏪',
                'pro': '👍',
                'anti': '🚫',
                'super': '⭐',
                'mega': '🔥',
                'ultra': '💎',
                'micro': '🤏',
                'mini': '🤏',
                'over': '⬆️',
                'under': '⬇️',
                'out': '📤',
                'in': '📥'
            },
            patterns: {
                hasNumbers: '🔢',
                hasUpperCase: '🔠',
                hasSymbols: '🔣',
                isQuestion: '❓',
                isExclamation: '❗',
                isAllCaps: '📢'
            }
        };
    }

    /**
     * Main conversion function
     */
    convert(text) {
        if (!text || typeof text !== 'string') {
            return 'Type something to see the magic! ✨';
        }

        // Check cache first
        const cacheKey = text.toLowerCase().trim();
        if (this.cache.has(cacheKey)) {
            this.stats.cacheHits++;
            return this.cache.get(cacheKey);
        }

        // Process text
        const result = this.processText(text);
        
        // Cache result
        this.cache.set(cacheKey, result);
        if (this.cache.size > 1000) {
            // Clear old cache entries
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }

        // Update stats
        this.stats.conversions++;
        this.stats.totalWords += text.split(' ').length;

        return result;
    }

    /**
     * Process text and convert to emojis
     */
    processText(text) {
        const words = text.split(/(\s+)/);
        const convertedWords = words.map(word => this.convertWord(word));
        return convertedWords.join('');
    }

    /**
     * Convert individual word to emoji
     */
    convertWord(word) {
        if (!word || /^\s+$/.test(word)) {
            return word;
        }

        const originalWord = word;
        const cleanWord = word.toLowerCase().replace(/[^\w]/g, '');
        
        if (!cleanWord) {
            return word;
        }

        // Direct mapping
        if (this.emojiMap[cleanWord]) {
            return `${originalWord} ${this.emojiMap[cleanWord]}`;
        }

        // Partial matching
        const partialMatch = this.findPartialMatch(cleanWord);
        if (partialMatch) {
            return `${originalWord} ${partialMatch}`;
        }

        // Context-based selection
        const contextEmoji = this.getContextEmoji(cleanWord);
        if (contextEmoji) {
            return `${originalWord} ${contextEmoji}`;
        }

        // Fallback selection
        const fallbackEmoji = this.getFallbackEmoji(cleanWord, originalWord);
        return `${originalWord} ${fallbackEmoji}`;
    }

    /**
     * Find partial matches for compound words
     */
    findPartialMatch(cleanWord) {
        for (const [key, emoji] of Object.entries(this.emojiMap)) {
            if (key.length > 2 && cleanWord.includes(key)) {
                return emoji;
            }
        }
        return null;
    }

    /**
     * Get emoji based on context patterns
     */
    getContextEmoji(cleanWord) {
        for (const [category, keywords] of Object.entries(this.contextPatterns)) {
            if (keywords.some(keyword => cleanWord.includes(keyword))) {
                // Return context-appropriate emoji
                switch (category) {
                    case 'technology': return '💻';
                    case 'emotions': return '😊';
                    case 'nature': return '🌿';
                    case 'food': return '🍽️';
                    case 'time': return '⏰';
                    case 'weather': return '🌤️';
                    case 'animals': return '🐾';
                    case 'actions': return '⚡';
                    case 'people': return '👥';
                    case 'places': return '📍';
                    default: return null;
                }
            }
        }
        return null;
    }

    /**
     * Get fallback emoji based on word characteristics
     */
    getFallbackEmoji(cleanWord, originalWord) {
        // Check for special patterns first
        if (/[0-9]/.test(cleanWord)) {
            return this.fallbackEmojis.patterns.hasNumbers;
        }
        
        if (/[A-Z]/.test(originalWord) && originalWord === originalWord.toUpperCase()) {
            return this.fallbackEmojis.patterns.isAllCaps;
        }
        
        if (originalWord.endsWith('?')) {
            return this.fallbackEmojis.patterns.isQuestion;
        }
        
        if (originalWord.endsWith('!')) {
            return this.fallbackEmojis.patterns.isExclamation;
        }

        // Check endings
        for (const [ending, emoji] of Object.entries(this.fallbackEmojis.endings)) {
            if (cleanWord.endsWith(ending)) {
                return emoji;
            }
        }

        // Check beginnings
        for (const [beginning, emoji] of Object.entries(this.fallbackEmojis.beginnings)) {
            if (cleanWord.startsWith(beginning)) {
                return emoji;
            }
        }

        // Length-based fallback
        const length = Math.min(cleanWord.length, 10);
        if (this.fallbackEmojis.length[length]) {
            return this.fallbackEmojis.length[length];
        }

        // Default fallback based on first letter
        const firstLetter = cleanWord[0].toLowerCase();
        const letterEmojis = {
            'a': '🅰️', 'b': '🅱️', 'c': '🌊', 'd': '🌅', 'e': '📧',
            'f': '🔥', 'g': '🌟', 'h': '🏠', 'i': '👁️', 'j': '🎭',
            'k': '👑', 'l': '💡', 'm': '🎵', 'n': '🌙', 'o': '⭕',
            'p': '🎉', 'q': '❓', 'r': '🚀', 's': '⭐', 't': '⏰',
            'u': '🆙', 'v': '✌️', 'w': '🌊', 'x': '❌', 'y': '💛',
            'z': '⚡'
        };

        return letterEmojis[firstLetter] || '✨';
    }

    /**
     * Convert with animation support
     */
    convertWithAnimation(text, callback) {
        const words = text.split(' ');
        let result = '';
        let index = 0;

        const convertNextWord = () => {
            if (index < words.length) {
                const convertedWord = this.convertWord(words[index]);
                result += (index > 0 ? ' ' : '') + convertedWord;
                
                if (callback) {
                    callback(result, index / words.length);
                }
                
                index++;
                setTimeout(convertNextWord, 100); // Animate word by word
            }
        };

        convertNextWord();
    }

    /**
     * Get conversion statistics
     */
    getStats() {
        return {
            ...this.stats,
            cacheSize: this.cache.size,
            averageWordsPerConversion: this.stats.conversions > 0 ? 
                Math.round(this.stats.totalWords / this.stats.conversions) : 0,
            cacheHitRate: this.stats.conversions > 0 ? 
                Math.round((this.stats.cacheHits / this.stats.conversions) * 100) : 0
        };
    }

    /**
     * Clear cache and reset stats
     */
    reset() {
        this.cache.clear();
        this.stats = {
            conversions: 0,
            cacheHits: 0,
            totalWords: 0
        };
    }

    /**
     * Add custom emoji mapping
     */
    addCustomMapping(word, emoji) {
        this.emojiMap[word.toLowerCase()] = emoji;
    }

    /**
     * Remove emoji mapping
     */
    removeMapping(word) {
        delete this.emojiMap[word.toLowerCase()];
    }

    /**
     * Get all available emoji mappings
     */
    getAllMappings() {
        return { ...this.emojiMap };
    }

    /**
     * Suggest emojis for a word
     */
    suggestEmojis(word) {
        const cleanWord = word.toLowerCase().replace(/[^\w]/g, '');
        const suggestions = [];

        // Direct match
        if (this.emojiMap[cleanWord]) {
            suggestions.push({
                emoji: this.emojiMap[cleanWord],
                reason: 'Direct match',
                confidence: 1.0
            });
        }

        // Partial matches
        for (const [key, emoji] of Object.entries(this.emojiMap)) {
            if (key !== cleanWord && (key.includes(cleanWord) || cleanWord.includes(key))) {
                suggestions.push({
                    emoji: emoji,
                    reason: `Partial match with "${key}"`,
                    confidence: Math.min(cleanWord.length, key.length) / Math.max(cleanWord.length, key.length)
                });
            }
        }

        // Fallback
        suggestions.push({
            emoji: this.getFallbackEmoji(cleanWord, word),
            reason: 'Fallback based on word characteristics',
            confidence: 0.5
        });

        return suggestions
            .sort((a, b) => b.confidence - a.confidence)
            .slice(0, 5); // Top 5 suggestions
    }

    /**
     * Batch convert multiple texts
     */
    batchConvert(texts) {
        return texts.map(text => ({
            original: text,
            converted: this.convert(text)
        }));
    }

    /**
     * Export configuration
     */
    exportConfig() {
        return {
            customMappings: { ...this.emojiMap },
            stats: { ...this.stats },
            version: '1.0.0',
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Import configuration
     */
    importConfig(config) {
        if (config.customMappings) {
            this.emojiMap = { ...this.emojiMap, ...config.customMappings };
        }
        if (config.stats) {
            this.stats = { ...this.stats, ...config.stats };
        }
    }
}

// Performance optimization for real-time conversion
class FastEmojiConverter extends EmojiConverter {
    constructor() {
        super();
        this.lastConversionTime = 0;
        this.debounceDelay = 100; // ms
        this.pendingConversion = null;
    }

    /**
     * Debounced conversion for real-time input
     */
    convertDebounced(text, callback) {
        if (this.pendingConversion) {
            clearTimeout(this.pendingConversion);
        }

        this.pendingConversion = setTimeout(() => {
            const result = this.convert(text);
            if (callback) {
                callback(result);
            }
            this.pendingConversion = null;
        }, this.debounceDelay);
    }

    /**
     * Immediate conversion with performance tracking
     */
    convertFast(text) {
        const startTime = performance.now();
        const result = this.convert(text);
        const endTime = performance.now();
        
        this.lastConversionTime = endTime - startTime;
        return result;
    }

    /**
     * Get performance metrics
     */
    getPerformanceStats() {
        return {
            ...this.getStats(),
            lastConversionTime: this.lastConversionTime,
            averageConversionTime: this.lastConversionTime // Could be expanded to track average
        };
    }
}

// Utility functions for DOM integration
const EmojiUtils = {
    /**
     * Apply emoji conversion to input element
     */
    attachToInput(inputElement, outputElement, options = {}) {
        const converter = new FastEmojiConverter();
        const { realTime = true, showStats = false } = options;

        const updateOutput = (converted) => {
            if (outputElement) {
                outputElement.innerHTML = converted;
                
                if (showStats) {
                    const stats = converter.getPerformanceStats();
                    console.log('Conversion Stats:', stats);
                }
            }
        };

        if (realTime) {
            inputElement.addEventListener('input', (e) => {
                converter.convertDebounced(e.target.value, updateOutput);
            });
        } else {
            inputElement.addEventListener('blur', (e) => {
                updateOutput(converter.convert(e.target.value));
            });
        }

        // Initial conversion
        if (inputElement.value) {
            updateOutput(converter.convert(inputElement.value));
        }

        return converter;
    },

    /**
     * Create emoji rain effect
     */
    createEmojiRain(container, options = {}) {
        const {
            emojis = ['😀', '🚀', '💬', '❤️', '🎉', '⭐', '🌟', '🔥', '👋'],
            duration = 5000,
            interval = 300,
            maxEmojis = 20
        } = options;

        let activeEmojis = 0;

        const createEmojiDrop = () => {
            if (activeEmojis >= maxEmojis) return;

            const emoji = document.createElement('span');
            emoji.textContent = emojis[Math.floor(Math.random() * emojis.length)];
            emoji.style.position = 'absolute';
            emoji.style.left = Math.random() * 100 + '%';
            emoji.style.fontSize = (Math.random() * 1.5 + 1) + 'rem';
            emoji.style.pointerEvents = 'none';
            emoji.style.zIndex = '1';
            emoji.style.animation = `emoji-fall ${duration}ms linear`;

            container.appendChild(emoji);
            activeEmojis++;

            // Remove emoji after animation
            setTimeout(() => {
                if (emoji.parentNode) {
                    emoji.parentNode.removeChild(emoji);
                    activeEmojis--;
                }
            }, duration);
        };

        // Create CSS animation if not exists
        if (!document.querySelector('#emoji-rain-styles')) {
            const style = document.createElement('style');
            style.id = 'emoji-rain-styles';
            style.textContent = `
                @keyframes emoji-fall {
                    0% {
                        transform: translateY(-100px) rotate(0deg);
                        opacity: 0;
                    }
                    10% {
                        opacity: 1;
                    }
                    90% {
                        opacity: 1;
                    }
                    100% {
                        transform: translateY(calc(100vh + 100px)) rotate(360deg);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        const rainInterval = setInterval(createEmojiDrop, interval);

        // Return cleanup function
        return () => {
            clearInterval(rainInterval);
            const emojiElements = container.querySelectorAll('span');
            emojiElements.forEach(el => {
                if (el.style.animation.includes('emoji-fall')) {
                    el.remove();
                }
            });
        };
    },

    /**
     * Animate text conversion
     */
    animateConversion(text, outputElement, options = {}) {
        const { speed = 100, showOriginal = true } = options;
        const converter = new EmojiConverter();
        const words = text.split(' ');
        let currentIndex = 0;

        outputElement.innerHTML = '';

        const animateNext = () => {
            if (currentIndex < words.length) {
                const word = words[currentIndex];
                const converted = converter.convertWord(word);
                
                const wordSpan = document.createElement('span');
                wordSpan.style.opacity = '0';
                wordSpan.style.transform = 'translateY(20px)';
                wordSpan.style.transition = 'all 0.3s ease';
                wordSpan.innerHTML = converted + (currentIndex < words.length - 1 ? ' ' : '');
                
                outputElement.appendChild(wordSpan);
                
                // Trigger animation
                setTimeout(() => {
                    wordSpan.style.opacity = '1';
                    wordSpan.style.transform = 'translateY(0)';
                }, 10);
                
                currentIndex++;
                setTimeout(animateNext, speed);
            }
        };

        animateNext();
    },

    /**
     * Copy converted text to clipboard
     */
    copyToClipboard(text) {
        const converter = new EmojiConverter();
        const converted = converter.convert(text);
        
        if (navigator.clipboard) {
            return navigator.clipboard.writeText(converted);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = converted;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return Promise.resolve();
        }
    }
};

// Initialize global emoji converter
window.EmojiConverter = EmojiConverter;
window.FastEmojiConverter = FastEmojiConverter;
window.EmojiUtils = EmojiUtils;

// Create global instance
window.emojiConverter = new FastEmojiConverter();

// Auto-initialize demo functionality if demo elements exist
document.addEventListener('DOMContentLoaded', function() {
    // Hero demo
    const heroDemo = document.getElementById('heroDemo');
    const heroOutput = document.getElementById('heroOutput');
    
    if (heroDemo && heroOutput) {
        EmojiUtils.attachToInput(heroDemo, heroOutput, {
            realTime: true,
            showStats: false
        });
    }

    // General demo inputs
    const demoInputs = document.querySelectorAll('[data-emoji-input]');
    demoInputs.forEach(input => {
        const outputId = input.dataset.emojiOutput;
        const output = document.getElementById(outputId);
        if (output) {
            EmojiUtils.attachToInput(input, output, {
                realTime: true,
                showStats: input.dataset.showStats === 'true'
            });
        }
    });

    // Create emoji rain effect if container exists
    const rainContainer = document.querySelector('.emoji-rain-container');
    if (rainContainer) {
        EmojiUtils.createEmojiRain(rainContainer, {
            interval: 500,
            duration: 8000,
            maxEmojis: 15
        });
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EmojiConverter, FastEmojiConverter, EmojiUtils };
}

// Performance monitoring
if (typeof window !== 'undefined' && window.performance) {
    window.emojiConverter.originalConvert = window.emojiConverter.convert;
    window.emojiConverter.convert = function(text) {
        const start = performance.now();
        const result = this.originalConvert(text);
        const end = performance.now();
        
        if (end - start > 10) { // Log slow conversions
            console.warn(`Slow emoji conversion: ${end - start}ms for "${text.substring(0, 50)}..."`);
        }
        
        return result;
    };
}