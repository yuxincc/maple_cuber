import pyautogui
import pytesseract
import time
import keyboard
import pygetwindow as gw
from PIL import Image

# ================ CONFIG ================
trial_run = True # set to true to only run once & preview the screenshot
skip_unknown_result = True # set to true to roll past unknown cube results
num_cubes = 500 # max number of times to roll
mode = "default"

# coordinates for cube result
x1, y1 = 870, 697 # top left
x2, y2 = 1032, 751 # bottom right

if mode == "npc":
    x1, y1 = 946, 720 # top left
    x2, y2 = 1199, 775 # bottom right

# ===== selection =====
desired_possibilities = [
    {"int": 3, "pureint": 2},
    {"magic": 1, "int": 2},
]

global cube_count

# INT double counts as pureint & int
# {"int": 3, "pureint": 1} 
# valid cube = int allstat allstat || int int allstat || int int int

stats_mapping = { 
    "puredex": ["DEX"],
    "purestr": ["STR"],
    "pureluk": ["LUK"],
    "pureint": ["INT"],
    "magic att": ["Magic ATT"],
    "ied": ["확 률 로 데 미 지"],
    "dex": ["DEX", "All Stats", "올스탯", "올"],
    "int": ["INT", "All Stats", "올스탯", "올"],
    "str": ["STR", "All Stats", "올스탯", "올"],
    "luk": ["LUK", "All Stats", "올스탯", "올"],
    "mp": ["Max MP", "최 대 MP", "올스탯", "올"],
    "hp": ["Max HP", "최 대 HP", "올스탯", "올"],
    "useless": ["하 미 퍼 바 디", "HP", "MP", "MAX"]
}

# ================ END OF CONFIG ================

def read_text(x1, y1, x2, y2, trial_run):
    time.sleep(3) # 3 seconds delay for cube options to load

    cube_ss = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
    new_x = (x2-x1)*100
    new_y = (y2-y1)*100
    cube_ss.resize((new_x, new_y))
    cube_ss = cube_ss.convert('L')

    if trial_run: 
        # saves screenshot and preview, check if coordinated
        cube_ss.save("screenshot.png")
        cube_ss.show()
    
    #  read stats in the image and convert them to text
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    text = pytesseract.image_to_string(cube_ss, lang='kor+eng+osd')
    
    filter_text = ("유 니 크", "레 전 드 리")
    cube_results = [option for option in text.split('\n') if option.strip() and option not in filter_text ]

    print(f"== Cube {cube_count} Result ==")
    print(cube_results)
    print()

    return cube_results

def use_new_cube():
    # Ctrl-P to use macro
    keyboard.press('ctrl')
    keyboard.press('p')
    keyboard.release('p')
    keyboard.release('ctrl')



def analyse_cube(cube_results, stats_mapping):
    analysis_result = dict()

    for cube_line in cube_results: # for every line within the cube result
        cube_line = cube_line.lower() # stat = STR: +12%

        for stat_name, value_list in stats_mapping.items():
            for val in value_list:
                if val.lower() in cube_line:
                    if stat_name in analysis_result:
                        analysis_result[stat_name] = analysis_result[stat_name] + 1
                    else:
                        analysis_result[stat_name] = 1

    return analysis_result

def check_cube_meet_requirement(analysis_result, desired_possibilities):  
    if sum(analysis_result.values()) < 3:
        if skip_unknown_result:
            return False
        
        print("unable to reliably detect", analysis_result)
        
        user_input = input("continue cubing? Y/N:")
        if user_input in ("Y", "y"):
            return False # continue cubing = cube doesnt meet user's requirement
        else:
            return True
    
    for acceptable_result in desired_possibilities:
        # check every requirement
        for stat, min_count in acceptable_result.items():
            if stat not in analysis_result:
                break
            if analysis_result[stat] < min_count:
                break
            print(f'cube matches {acceptable_result}')
            return True
            
    return False

print("==Requirements==")
for r in desired_possibilities:
    print(r)
print()

# step 1: loop every cube
for i in range(num_cubes):
    cube_count = i+1 
    # use_new_cube()
    cube_results = read_text(x1, y1, x2, y2, trial_run) # step 2a: read cube results
    
    cube_stats = analyse_cube(cube_results, stats_mapping)
    keep_cube = check_cube_meet_requirement(cube_stats, desired_possibilities)

    if keep_cube: 
        print("✓ Cube retained")
        print('\a')
        break

    if trial_run:
        break
