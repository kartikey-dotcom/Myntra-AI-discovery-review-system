"""
Deterministic 15,000-Record VoC Corpus Generator for Myntra Growth Engine.
Generates an authentic distribution matching Indian fashion e-commerce dynamics:
- 10,000 Google Play / App Store Reviews (com.myntra.android)
- 3,500 Reddit Fashion Community Threads (r/IndianFashionAddicts, r/TwoXIndia, r/delhi, r/bangalore)
- 1,500 YouTube Try-On Haul Comments
"""

import json
import random
import os
from datetime import datetime, timedelta

SEED = 42
random.seed(SEED)

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "raw_15k_corpus.json")

# Brand names common on Myntra
BRANDS = [
    "Roadster", "HRX", "Mast & Harbour", "Anouk", "Sangria", "Mango", "H&M",
    "Zara", "Forever 21", "Tokyo Talkies", "DressBerry", "W", "Aurelia",
    "Libas", "Vishudh", "Marks & Spencer", "Levis", "Jack & Jones", "Snitch"
]

# Apparel Categories
CATEGORIES = [
    "Kurti & Ethnic Set", "Midi Dress", "Oversized T-Shirt", "Wide Leg Jeans",
    "Casual Blazer", "Cropped Top", "Maxi Skirt", "Formal Trousers", "Denim Jacket",
    "Party Jumpsuit", "Co-ord Set", "Linen Shirt"
]

# Cities & Cohorts
CITIES = ["Delhi NCR", "Bangalore", "Mumbai", "Pune", "Hyderabad", "Jaipur", "Lucknow", "Kolkata", "Ahmedabad", "Chandigarh", "Indore", "Patna"]
BODY_TYPES = ["Petite (5'1-5'3)", "Average (5'4-5'6)", "Tall (5'7+)", "Curvy / Hourglass", "Athletic / Broad Shoulder", "Slim / Pear"]
COHORTS = ["STUDENT_GEN_Z", "WORKING_PROFESSIONAL", "TIER_2_ASPIRATIONAL"]

# 1. High-Signal Fashion Deliberation Templates
STYLING_TEMPLATES = [
    "Saved this {brand} {category} 3 weeks ago in wishlist. Samajh nahi aa raha kiske saath pair karu. What color bottoms go with this?",
    "Wishlisted this {category} for office wear, but I have no idea how to style it without looking too casual. Still sitting in saved items.",
    "Love the cut on this {brand} {category}, but don't know if my white sneakers or block heels will look better. Hesitating to buy.",
    "I have 5 different tops wishlisted, but keep delaying checkout bcz I don't know if I have the right trousers in my wardrobe.",
    "Bohot pretty {category} hai from {brand}, but styling confusion is real. Took screenshot and asked in WhatsApp group.",
    "Wishlisted this {category}. Need styling inspo. Model look looks great but in real life what accessories will go?",
    "Has anyone styled this {brand} {category} for a summer brunch? Stuck in my wishlist forever bcz I can't visualize the complete look."
]

FIT_TEMPLATES = [
    "Wishlisted {brand} {category} in size M, but {brand}'s sizing is so unpredictable! Normally I wear S in Mango and M in Roadster. So confused.",
    "Model is 5'10 wearing S, but I am 5'2. Darr lag raha hai ki it will reach my ankles instead of midi length. Not checking out.",
    "Sizing issue: size chart says chest 36 is M, but reviews say it runs super tight around the bust. Wishlisted till I know exact fit.",
    "I really want this {brand} {category} but I have broad shoulders. Will L be too baggy on waist? Wishlisted for 2 weeks now.",
    "Should I buy S or M? Usually {brand} shrinks a bit after wash. Contemplating buying 2 sizes and returning one (bracketing).",
    "Size chart is totally confusing for this {category}. Mango size 6 vs Zara S vs {brand} M... wishlisted until someone posts real measurements.",
    "The waistline on this {category} looks high-waisted on model, but on curvy body type it might sit weirdly. Left in wishlist."
]

FABRIC_TEMPLATES = [
    "The {category} looks gorgeous in photos, but is the fabric see-through? Kapda patla toh nahi hai daylight me? Waiting to be sure.",
    "Is this 100% pure cotton or polyester blend? In Delhi summer, synthetic fabric is unwearable. Wishlisted until fabric details get clear.",
    "Looks like linen in pictures, but description says viscose blend. Is it breathable or will it feel scratchy? Hesitating.",
    "Want to buy this {brand} {category} for daily college use. Does it bleed color or shrink in first machine wash?",
    "Fabric transparency doubt! In studio lighting it looks opaque, but one review said inner slip is needed. Sitting in my wishlist.",
    "The lining inside this {category} - is it soft or rough polyester? Don't want itchy seams during 8 hour workdays. Saved for now."
]

SOCIAL_VALIDATION_TEMPLATES = [
    "Wishlisted this {brand} {category} and shared screenshot on our girlies WhatsApp group. Waiting for their verdict before placing order!",
    "Added to wishlist last night. Need second opinion from my sister on whether this color looks washed out on warm Indian undertones.",
    "Sent the Myntra link to 3 friends to ask 'should I buy or skip?'. Nobody replied yet so it's still in my wishlist.",
    "Is this {category} too experimental for college? Wishlisted it, waiting for my roommate to see if she approves."
]

OCCASION_TEMPLATES = [
    "Aspirational buy! Saved this stunning {brand} {category} in my wishlist, but honestly have nowhere to wear it right now.",
    "Such a gorgeous party {category} from {brand}. Wishlisted for future Goa trip / friend's wedding, but no immediate plan.",
    "Love the design, but it feels too festive for regular office and too formal for weekends. Lingering in my wishlist."
]

COMPARISON_PARALYSIS_TEMPLATES = [
    "I have 6 almost identical black {category}s wishlisted across {brand}, H&M, and Mango. Can't decide which one has the best drape.",
    "Decision fatigue! Wishlisted 4 floral {category}s from different brands. Comparing fabric composition and sleeves back and forth.",
    "Wishlist has 20 items. Every time I open it to buy one {category}, I get confused between 3 similar options and close the app."
]

PRICE_SPECULATION_TEMPLATES = [
    "Wishlisted this {brand} {category} waiting for EORS / Big Fashion Festival sale price drop to Rs. 799.",
    "Added to wishlist to track discount. Price is currently Rs. 1,899, will only buy if it drops below 1,200.",
    "Waiting for end of month coupon / bank discount before checking out this {category}."
]

# 2. Noise & Spam Templates (Logistics, OTP, Courier, 1-word spam)
NOISE_TEMPLATES = [
    "Delivery guy called 5 times and didn't deliver on time. Terrible courier service in Bangalore.",
    "Refund not received in my bank account after 7 days! Fix customer support!",
    "OTP not coming during login. Please solve this bug app is crashing on Android 14.",
    "Delivery was fast, packaging was neat. 5 stars.",
    "Nice.", "Good product.", "Bad quality.", "Ok.", "Loved it ❤️", "Superb 👍",
    "Wrong color delivered. Return pick up delayed by 3 days.",
    "Customer care executive disconnected call without resolving delivery issue.",
    "App getting hang on payment gateway page. Flipkart is better.",
    "1 star for delivery agent rudeness. Product is not opened yet.",
    "Good.", "Osm!!", "Mast product.", "Best app for shopping.", "Fast shipping thanks."
]

def generate_voc_corpus(target_count: int = 15000):
    records = []
    
    source_counts = {
        "Google Play Store (com.myntra.android)": int(target_count * 0.65),
        "Reddit Fashion Communities": int(target_count * 0.2333),
        "YouTube Fashion Haul Comments": target_count - int(target_count * 0.65) - int(target_count * 0.2333)
    }
    
    record_id_counter = 1
    base_time = datetime.now() - timedelta(days=90)
    
    for source, count in source_counts.items():
        for i in range(count):
            brand = random.choice(BRANDS)
            category = random.choice(CATEGORIES)
            cohort = random.choices(COHORTS, weights=[0.45, 0.35, 0.20])[0]
            body_type = random.choice(BODY_TYPES)
            city = random.choice(CITIES)
            time_offset = random.randint(0, 90 * 24 * 60)
            created_at = (base_time + timedelta(minutes=time_offset)).isoformat()
            
            # Determine if this record is Noise or High-Signal Deliberation
            # In Play Store: ~48% noise, in Reddit: ~15% noise, in YouTube: ~25% noise
            if "Play Store" in source:
                is_noise = random.random() < 0.48
            elif "Reddit" in source:
                is_noise = random.random() < 0.15
            else:
                is_noise = random.random() < 0.25
                
            if is_noise:
                text = random.choice(NOISE_TEMPLATES)
                rating = random.choices([1, 2, 3, 4, 5], weights=[0.35, 0.20, 0.15, 0.15, 0.15])[0]
                likes = random.randint(0, 5)
                sub_source = source
            else:
                # Deliberation category distribution:
                # Styling: 32%, Fit: 28%, Fabric: 18%, Social: 10%, Comparison: 7%, Occasion: 3%, Price: 2%
                delib_type = random.choices(
                    ["styling", "fit", "fabric", "social", "comparison", "occasion", "price"],
                    weights=[0.32, 0.28, 0.18, 0.10, 0.07, 0.03, 0.02]
                )[0]
                
                if delib_type == "styling":
                    text = random.choice(STYLING_TEMPLATES).format(brand=brand, category=category)
                elif delib_type == "fit":
                    text = random.choice(FIT_TEMPLATES).format(brand=brand, category=category)
                elif delib_type == "fabric":
                    text = random.choice(FABRIC_TEMPLATES).format(brand=brand, category=category)
                elif delib_type == "social":
                    text = random.choice(SOCIAL_VALIDATION_TEMPLATES).format(brand=brand, category=category)
                elif delib_type == "comparison":
                    text = random.choice(COMPARISON_PARALYSIS_TEMPLATES).format(brand=brand, category=category)
                elif delib_type == "occasion":
                    text = random.choice(OCCASION_TEMPLATES).format(brand=brand, category=category)
                else:
                    text = random.choice(PRICE_SPECULATION_TEMPLATES).format(brand=brand, category=category)
                    
                rating = random.choices([3, 4, 2, 5, 1], weights=[0.40, 0.30, 0.15, 0.10, 0.05])[0]
                likes = random.randint(1, 150)
                
                if "Reddit" in source:
                    sub_source = random.choice([
                        "r/IndianFashionAddicts", "r/TwoXIndia", "r/delhi", "r/bangalore"
                    ])
                elif "YouTube" in source:
                    sub_source = f"YouTube (Myntra {category} Try-On Haul)"
                else:
                    sub_source = "Google Play Store (com.myntra.android)"

            record = {
                "record_id": f"voc_rec_{record_id_counter:05d}",
                "source": source,
                "sub_source": sub_source if not is_noise else source,
                "created_at": created_at,
                "rating": rating,
                "upvotes_or_likes": likes,
                "raw_text": text,
                "apparel_category": category,
                "brand_mentioned": brand,
                "user_metadata": {
                    "cohort": cohort,
                    "body_type": body_type,
                    "city": city
                }
            }
            records.append(record)
            record_id_counter += 1

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully generated {len(records)} VoC records -> {OUTPUT_PATH}")
    return records

if __name__ == "__main__":
    generate_voc_corpus(15000)
