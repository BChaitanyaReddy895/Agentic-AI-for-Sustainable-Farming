"""
Comprehensive accuracy test suite for the AgriSmart Hybrid Recommendation Engine.
Tests multiple scenarios to validate that the custom engine produces correct,
differentiated, and preference-aware recommendations.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.custom_engine import AgriSmartEngine

engine = AgriSmartEngine()

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {name} {detail}")
    else:
        FAIL += 1
        print(f"  FAIL  {name} {detail}")

print("=" * 70)
print("AGRISMART HYBRID ENGINE — ACCURACY TEST SUITE")
print("=" * 70)

# ─── TEST 1: Preference differentiation ──────────────────────────
print("\n--- TEST 1: Crop preference differentiation ---")
prefs = {}
for pref in ["Grains", "Vegetables", "Fruits", "Pulses", "Cash Crops", "Oilseeds", "Spices"]:
    r = engine.recommend(ph=6.5, temperature=25, rainfall=80, nitrogen=0, phosphorus=0, potassium=0, crop_preference=pref)
    prefs[pref] = r["recommended_crop"]
    print(f"  {pref:15s} -> {r['recommended_crop']:12s} (score={r['final_score']}, conf={r['confidence']}%)")

unique_crops = len(set(prefs.values()))
check("Different prefs produce different crops", unique_crops >= 5, f"({unique_crops}/7 unique)")

# ─── TEST 2: Grains — correct crops ─────────────────────────────
print("\n--- TEST 2: Grains preference maps to grain crops ---")
r = engine.recommend(ph=6.5, temperature=25, rainfall=80, nitrogen=0, phosphorus=0, potassium=0, crop_preference="Grains")
check("Grains -> grain crop", r["recommended_crop"].lower() in ["rice","wheat","corn","maize","millet","barley","oats","sorghum"], f"got {r['recommended_crop']}")

# ─── TEST 3: Vegetables ─────────────────────────────────────────
print("\n--- TEST 3: Vegetables preference ---")
r = engine.recommend(ph=6.5, temperature=25, rainfall=80, nitrogen=0, phosphorus=0, potassium=0, crop_preference="Vegetables")
check("Vegetables -> vegetable crop", r["recommended_crop"].lower() in ["tomato","potato","onion"], f"got {r['recommended_crop']}")

# ─── TEST 4: Cash Crops ─────────────────────────────────────────
print("\n--- TEST 4: Cash Crops preference (warm conditions) ---")
r = engine.recommend(ph=7.0, temperature=30, rainfall=120, nitrogen=80, phosphorus=30, potassium=30, crop_preference="Cash Crops")
check("Cash Crops -> cash crop", r["recommended_crop"].lower() in ["cotton","sugarcane","jute","tea","coffee"], f"got {r['recommended_crop']}")

# ─── TEST 5: Oilseeds ───────────────────────────────────────────
print("\n--- TEST 5: Oilseeds preference ---")
r = engine.recommend(ph=6.5, temperature=25, rainfall=70, nitrogen=0, phosphorus=0, potassium=0, crop_preference="Oilseeds")
check("Oilseeds -> oilseed crop", r["recommended_crop"].lower() in ["mustard","sunflower","sesame","groundnut"], f"got {r['recommended_crop']}")

# ─── TEST 6: Fruits ──────────────────────────────────────────────
print("\n--- TEST 6: Fruits preference (tropical) ---")
r = engine.recommend(ph=6.5, temperature=28, rainfall=150, nitrogen=100, phosphorus=40, potassium=100, crop_preference="Fruits")
check("Fruits -> banana", r["recommended_crop"].lower() == "banana", f"got {r['recommended_crop']}")

# ─── TEST 7: Spices ──────────────────────────────────────────────
print("\n--- TEST 7: Spices preference ---")
r = engine.recommend(ph=6.0, temperature=28, rainfall=180, nitrogen=40, phosphorus=25, potassium=50, crop_preference="Spices")
check("Spices -> turmeric", r["recommended_crop"].lower() == "turmeric", f"got {r['recommended_crop']}")

# ─── TEST 8: Tropical conditions favour rice ─────────────────────
print("\n--- TEST 8: Tropical wet (no preference) ---")
r = engine.recommend(ph=6.0, temperature=30, rainfall=200, nitrogen=80, phosphorus=30, potassium=30, crop_preference=None)
check("Tropical -> rice or sugarcane", r["recommended_crop"].lower() in ["rice","sugarcane","jute","banana"], f"got {r['recommended_crop']}")

# ─── TEST 9: Cold dry => rabi crops ──────────────────────────────
print("\n--- TEST 9: Cold dry conditions ---")
r = engine.recommend(ph=7.0, temperature=15, rainfall=40, nitrogen=80, phosphorus=40, potassium=30, crop_preference=None)
check("Cold/dry -> rabi crop", r["recommended_crop"].lower() in ["wheat","barley","mustard","chickpea","lentil","potato","oats","onion"], f"got {r['recommended_crop']}")

# ─── TEST 10: Score explanation exists ────────────────────────────
print("\n--- TEST 10: Explainability check ---")
r = engine.recommend(ph=6.5, temperature=25, rainfall=80, nitrogen=0, phosphorus=0, potassium=0, crop_preference="Grains")
check("Has score explanations", len(r.get("score_explanation", [])) >= 3, f"({len(r.get('score_explanation',[]))} lines)")
check("Has layer scores", bool(r.get("layer_scores")), f"{list(r.get('layer_scores',{}).keys())}")
check("Has alternatives", len(r.get("alternatives", [])) >= 2, f"({len(r.get('alternatives',[]))} alternatives)")
check("Has comparative data", bool(r.get("comparative", {}).get("all_categories")), "")
check("Has confidence %", r.get("confidence", 0) > 0 and r.get("confidence", 0) <= 100, f"({r.get('confidence')}%)")
check("Has data points count", r.get("data_points_analysed", 0) > 100000, f"({r.get('data_points_analysed',0):,})")

# ─── TEST 11: Comparative section completeness ───────────────────
print("\n--- TEST 11: Comparative data structure ---")
comp = r.get("comparative", {})
check("Has preferred_category list", len(comp.get("preferred_category", [])) >= 1, f"({len(comp.get('preferred_category',[]))} crops)")
check("Has all_categories dict", len(comp.get("all_categories", {})) >= 5, f"({len(comp.get('all_categories',{}))} categories)")
check("Has top_overall list", len(comp.get("top_overall", [])) >= 5, f"({len(comp.get('top_overall',[]))} crops)")

# ─── TEST 12: NPK sensitivity ────────────────────────────────────
print("\n--- TEST 12: NPK sensitivity (high nitrogen changes recommendation) ---")
r_no_npk = engine.recommend(ph=6.5, temperature=25, rainfall=80, nitrogen=0, phosphorus=0, potassium=0, crop_preference="Grains")
r_high_n = engine.recommend(ph=6.5, temperature=25, rainfall=80, nitrogen=120, phosphorus=50, potassium=50, crop_preference="Grains")
check("NPK=0 vs NPK=120/50/50 produce different scores",
      r_no_npk["final_score"] != r_high_n["final_score"],
      f"(NPK=0 score={r_no_npk['final_score']}, high-NPK score={r_high_n['final_score']})")

# ─── TEST 13: Season awareness ────────────────────────────────────
print("\n--- TEST 13: Season bonus present ---")
r = engine.recommend(ph=6.5, temperature=25, rainfall=80, nitrogen=0, phosphorus=0, potassium=0, crop_preference="Grains")
check("Layer scores include season", "season" in r.get("layer_scores", {}), "")
check("Season score is 0 or 1", r["layer_scores"].get("season", -1) in [0, 0.0, 1, 1.0], f"(={r['layer_scores'].get('season')})")

# ─── SUMMARY ─────────────────────────────────────────────────────
print("\n" + "=" * 70)
total = PASS + FAIL
pct = round(PASS/total*100, 1) if total else 0
print(f"RESULTS: {PASS}/{total} passed ({pct}%)")
if FAIL == 0:
    print("ALL TESTS PASSED")
else:
    print(f"{FAIL} test(s) failed")
print("=" * 70)
