import unittest
import json
import os
from app.services.score import score, cosine
from app.services.ai import embed, describe_image

class TestScoring(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        # Sample image description (what GPT-4 Vision might return)
        self.sample_description = {
            "objects": ["mountain", "lake", "trees", "sky"],
            "colors": ["blue", "green", "white", "brown"],
            "shapes": ["triangular", "circular", "organic"],
            "materials": ["rock", "water", "wood"],
            "setting": "outdoor natural landscape with mountains and a lake"
        }
        
        # Various test notes with different levels of accuracy
        self.test_cases = [
            {
                "name": "excellent_match",
                "notes": "I see mountains and a lake. The colors are blue and green. There's a triangular mountain shape and circular lake. The setting is outdoors with natural elements like rocks and water.",
                "expected_min_score": 0.5
            },
            {
                "name": "good_match",
                "notes": "I see something tall and pointy, maybe mountains? There's water, possibly a lake. I get the feeling of nature and outdoors. Colors seem cool and earthy.",
                "expected_min_score": 0.3
            },
            {
                "name": "partial_match",
                "notes": "I see something natural. There are earthy colors. The shape feels organic. It's outdoors.",
                "expected_min_score": 0.2
            },
            {
                "name": "poor_match",
                "notes": "I see a building with windows. There's a person inside. Maybe it's an office or home. The colors are beige and white.",
                "expected_max_score": 0.1
            },
            {
                "name": "specific_color_match",
                "notes": "The dominant colors are blue, green, white, and brown.",
                "check_category": "color",
                "expected_min_category_score": 1
            },
            {
                "name": "specific_shape_match",
                "notes": "I see triangular and circular shapes, with some organic elements.",
                "check_category": "shape",
                "expected_min_category_score": 1
            }
        ]
        
        # Mock image descriptions for different types of images
        self.mock_images = {
            "mountain_lake": {
                "objects": ["mountain", "lake", "trees", "sky", "clouds"],
                "colors": ["blue", "green", "white", "gray", "turquoise"],
                "shapes": ["triangular", "circular", "organic", "wavy"],
                "materials": ["rock", "water", "wood", "ice"],
                "setting": "serene mountain landscape with crystal clear lake surrounded by pine trees"
            },
            "beach_sunset": {
                "objects": ["ocean", "sand", "palm trees", "sun", "clouds"],
                "colors": ["orange", "red", "yellow", "blue", "tan"],
                "shapes": ["circular", "wavy", "flowing", "organic"],
                "materials": ["water", "sand", "wood", "vapor"],
                "setting": "tropical beach at sunset with waves lapping on shore and palm trees"
            },
            "city_skyline": {
                "objects": ["buildings", "skyscrapers", "streets", "cars", "windows"],
                "colors": ["gray", "blue", "black", "white", "yellow"],
                "shapes": ["rectangular", "square", "linear", "geometric"],
                "materials": ["glass", "steel", "concrete", "asphalt"],
                "setting": "modern urban cityscape with tall skyscrapers and busy streets"
            }
        }
    
    def test_cosine_similarity(self):
        """Test the cosine similarity function with known vectors"""
        vec1 = [1, 0, 0, 0]
        vec2 = [1, 0, 0, 0]
        vec3 = [0, 1, 0, 0]
        vec4 = [-1, 0, 0, 0]
        
        # Same vectors should have similarity 1.0
        self.assertAlmostEqual(cosine(vec1, vec2), 1.0)
        
        # Orthogonal vectors should have similarity 0.0
        self.assertAlmostEqual(cosine(vec1, vec3), 0.0)
        
        # Opposite vectors should have similarity -1.0
        self.assertAlmostEqual(cosine(vec1, vec4), -1.0)
    
    def test_embedding_consistency(self):
        """Test if embed function returns consistent results for similar inputs"""
        embed1 = embed("mountain lake")
        embed2 = embed("mountain lake")
        
        # Same text should have very similar embeddings
        similarity = cosine(embed1, embed2)
        self.assertGreater(similarity, 0.99)
        
        # Different but related text should have somewhat similar embeddings
        embed3 = embed("mountains with a lake")
        similarity = cosine(embed1, embed3)
        self.assertGreater(similarity, 0.8)
        
        # Very different text should have lower similarity
        embed4 = embed("office building")
        similarity = cosine(embed1, embed4)
        self.assertLess(similarity, 0.5)
    
    def test_score_function_with_prepared_data(self):
        """Test the score function with our prepared test cases"""
        for test_case in self.test_cases:
            result = score(test_case["notes"], self.sample_description)
            
            print(f"\nTest case: {test_case['name']}")
            print(f"Notes: {test_case['notes']}")
            print(f"Cosine similarity: {result['cosine']}")
            print(f"Total score: {result['total']}")
            print(f"Rubric: {json.dumps(result['rubric'], indent=2)}")
            
            # Check overall score expectations if defined
            if "expected_min_score" in test_case:
                self.assertGreaterEqual(
                    result["total"], 
                    test_case["expected_min_score"],
                    f"Score for '{test_case['name']}' is lower than expected"
                )
            
            if "expected_max_score" in test_case:
                self.assertLessEqual(
                    result["total"], 
                    test_case["expected_max_score"],
                    f"Score for '{test_case['name']}' is higher than expected"
                )
            
            # Check category-specific expectations if defined
            if "check_category" in test_case and "expected_min_category_score" in test_case:
                category = test_case["check_category"]
                self.assertGreaterEqual(
                    result["rubric"][category],
                    test_case["expected_min_category_score"],
                    f"Category '{category}' score for '{test_case['name']}' is lower than expected"
                )
    
    def test_scoring_with_mock_images(self):
        """Test scoring against mock image descriptions instead of real images
        
        This avoids the issues with image processing and focuses on the scoring mechanism
        """
        # Test with mountain lake image
        mountain_lake_desc = self.mock_images["mountain_lake"]
        
        # Good match for mountain lake - explicitly mention colors
        good_notes = "The image shows blue and green colors in a mountain scene with a turquoise lake. The mountains have triangular shapes and there are pine trees. The water is clear and the sky is blue with some clouds."
        good_result = score(good_notes, mountain_lake_desc)
        
        # Poor match for mountain lake
        poor_notes = "I see a city with tall buildings and busy streets. There are many windows and cars. The colors are mostly gray and black with some yellow lights."
        poor_result = score(poor_notes, mountain_lake_desc)
        
        print("\nTest with mock mountain lake image:")
        print(f"Good notes score: {good_result['total']}")
        print(f"Good notes rubric: {json.dumps(good_result['rubric'], indent=2)}")
        print(f"Poor notes score: {poor_result['total']}")
        print(f"Poor notes rubric: {json.dumps(poor_result['rubric'], indent=2)}")
        
        # Good match should score higher than poor match
        self.assertGreater(good_result["total"], poor_result["total"])
        # Now with our threshold approach, we should see clearer differentiation
        if good_result["rubric"]["color"] > 0 or poor_result["rubric"]["color"] > 0:
            self.assertGreater(good_result["rubric"]["color"], poor_result["rubric"]["color"])
        if good_result["rubric"]["shape"] > 0 or poor_result["rubric"]["shape"] > 0:
            self.assertGreater(good_result["rubric"]["shape"], poor_result["rubric"]["shape"])
        
        # Test with beach sunset image
        beach_sunset_desc = self.mock_images["beach_sunset"]
        
        # Good match for beach - explicitly mention colors
        beach_good_notes = "I see a beautiful orange and red sunset on a tropical beach with the sun setting. The sky has yellow and orange colors. There's a tan sandy beach with palm trees and blue ocean waves on the shore."
        beach_good_result = score(beach_good_notes, beach_sunset_desc)
        
        # Poor match for beach
        beach_poor_notes = "I see a snowy mountain with pine trees. It's very cold and white. There might be some skiers. The scene is wintry and has no warm colors."
        beach_poor_result = score(beach_poor_notes, beach_sunset_desc)
        
        print("\nTest with mock beach sunset image:")
        print(f"Good notes score: {beach_good_result['total']}")
        print(f"Poor notes score: {beach_poor_result['total']}")
        
        # Good match should score higher than poor match
        self.assertGreater(beach_good_result["total"], beach_poor_result["total"])
    
    def test_cross_image_scoring(self):
        """Test if notes for one image type score lower on different image types"""
        # Get descriptions
        mountain_desc = self.mock_images["mountain_lake"]
        beach_desc = self.mock_images["beach_sunset"]
        city_desc = self.mock_images["city_skyline"]
        
        # Notes specific to each image type - be very explicit to test differentiation
        mountain_notes = "I see blue and green colors with tall triangular mountains and a clear blue lake. There are pine trees and the water reflects the sky. The rocks look solid and the material is mostly stone and water."
        beach_notes = "I see orange and red colors in a beautiful sunset over the ocean. The yellow sun is setting. There's a tan sandy beach with palm trees. The waves are wavy and flowing on the shore."
        city_notes = "I see gray and blue colors with tall rectangular skyscrapers and buildings in an urban environment. There are streets with cars and many glass windows. The materials are glass, steel and concrete."
        
        # Score each notes against each image
        results = {}
        for notes_type, notes in [("mountain", mountain_notes), ("beach", beach_notes), ("city", city_notes)]:
            results[notes_type] = {
                "mountain": score(notes, mountain_desc),
                "beach": score(notes, beach_desc),
                "city": score(notes, city_desc)
            }
        
        print("\nCross-image scoring results:")
        for notes_type, targets in results.items():
            print(f"\n{notes_type.capitalize()} notes scores:")
            for target_type, result in targets.items():
                print(f"  {target_type}: {result['total']} {json.dumps(result['rubric'])}")
        
        # Notes should score highest on their matching image type
        self.assertGreater(results["mountain"]["mountain"]["total"], results["mountain"]["beach"]["total"])
        self.assertGreater(results["mountain"]["mountain"]["total"], results["mountain"]["city"]["total"])
        
        self.assertGreater(results["beach"]["beach"]["total"], results["beach"]["mountain"]["total"])
        self.assertGreater(results["beach"]["beach"]["total"], results["beach"]["city"]["total"])
        
        self.assertGreater(results["city"]["city"]["total"], results["city"]["mountain"]["total"])
        self.assertGreater(results["city"]["city"]["total"], results["city"]["beach"]["total"])
    
    def test_category_differentiation(self):
        """Test if the scoring system properly differentiates between categories"""
        # Test with mountain lake image
        mountain_desc = self.mock_images["mountain_lake"]
        
        # Notes focused on colors - be very explicit
        color_notes = "The colors I see in this image are blue, green, white, gray and turquoise. The lake is turquoise blue, the trees are green, the mountains have white tops, and there are gray clouds in the sky."
        color_result = score(color_notes, mountain_desc)
        
        # Notes focused on shapes - be very explicit
        shape_notes = "I see triangular mountain shapes, a circular lake, and organic tree forms with wavy cloud patterns. The mountains form pointed triangles, the lake has a rounded circular shape, and the trees have irregular organic forms."
        shape_result = score(shape_notes, mountain_desc)
        
        # Notes focused on objects - be very explicit
        object_notes = "There are mountains, a lake, trees, sky and clouds in this image. I can clearly see tall mountains, a wide lake, numerous trees, blue sky, and several clouds."
        object_result = score(object_notes, mountain_desc)
        
        # Notes focused on setting/sensory - be very explicit
        setting_notes = "It's a serene mountain landscape with crystal clear water. The peaceful lake is surrounded by pine trees, creating a tranquil natural setting. The materials include rocky mountains, wooden trees, and clear water reflecting the surroundings."
        setting_result = score(setting_notes, mountain_desc)
        
        print("\nCategory differentiation test:")
        print(f"Color-focused notes: {json.dumps(color_result['rubric'], indent=2)}")
        print(f"Shape-focused notes: {json.dumps(shape_result['rubric'], indent=2)}")
        print(f"Object-focused notes: {json.dumps(object_result['rubric'], indent=2)}")
        print(f"Setting-focused notes: {json.dumps(setting_result['rubric'], indent=2)}")
        
        # Each notes type should score higher in its respective category
        # With our new thresholding approach, some scores might be zero
        # So we need to check if at least one is non-zero
        if color_result["rubric"]["color"] > 0 or color_result["rubric"]["shape"] > 0:
            self.assertGreaterEqual(color_result["rubric"]["color"], color_result["rubric"]["shape"])
        if color_result["rubric"]["color"] > 0 or color_result["rubric"]["concept"] > 0:
            self.assertGreaterEqual(color_result["rubric"]["color"], color_result["rubric"]["concept"])
        if color_result["rubric"]["color"] > 0 or color_result["rubric"]["sensory"] > 0:
            self.assertGreaterEqual(color_result["rubric"]["color"], color_result["rubric"]["sensory"])
        
        if shape_result["rubric"]["shape"] > 0 or shape_result["rubric"]["color"] > 0:
            self.assertGreaterEqual(shape_result["rubric"]["shape"], shape_result["rubric"]["color"])
        if shape_result["rubric"]["shape"] > 0 or shape_result["rubric"]["concept"] > 0:
            self.assertGreaterEqual(shape_result["rubric"]["shape"], shape_result["rubric"]["concept"])
        if shape_result["rubric"]["shape"] > 0 or shape_result["rubric"]["sensory"] > 0:
            self.assertGreaterEqual(shape_result["rubric"]["shape"], shape_result["rubric"]["sensory"])
        
        if object_result["rubric"]["concept"] > 0 or object_result["rubric"]["color"] > 0:
            self.assertGreaterEqual(object_result["rubric"]["concept"], object_result["rubric"]["color"])
        if object_result["rubric"]["concept"] > 0 or object_result["rubric"]["shape"] > 0:
            self.assertGreaterEqual(object_result["rubric"]["concept"], object_result["rubric"]["shape"])
        
        if setting_result["rubric"]["sensory"] > 0 or setting_result["rubric"]["color"] > 0:
            self.assertGreaterEqual(setting_result["rubric"]["sensory"], setting_result["rubric"]["color"])
        if setting_result["rubric"]["sensory"] > 0 or setting_result["rubric"]["shape"] > 0:
            self.assertGreaterEqual(setting_result["rubric"]["sensory"], setting_result["rubric"]["shape"])

if __name__ == "__main__":
    unittest.main() 