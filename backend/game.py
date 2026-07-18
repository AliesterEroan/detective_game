import pygame
import os
import sys
import json
import random
import logging
import traceback
import subprocess

# ----------------------------------------------------
# AUTOMATED PATH ALIGNMENT MATRIX
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    from backend.engine.game_controller import DetectiveGameController
    from backend.engine.anime_minigame import run_generator_minigame
except ModuleNotFoundError:
    try:
        from engine.game_controller import DetectiveGameController
        from engine.anime_minigame import run_generator_minigame
    except ModuleNotFoundError:
        class DetectiveGameController:
            def __init__(self): self.state = {"logs": []}
            def start_new_case(self): pass
        def run_generator_minigame(): pass

# ----------------------------------------------------
# SYSTEM LOGGING PIPELINE
# ----------------------------------------------------
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

TXT_LOG_PATH = os.path.join(LOG_DIR, 'game_errors.txt')
logging.basicConfig(
    filename=TXT_LOG_PATH, level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s', filemode='w'
)

try:
    pygame.init()
    pygame.mixer.init()
except Exception as err:
    logging.critical(f"Core hardware module boot failure: {err}")
    raise

# Window Specifications
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
FPS = 60

# Palette Configurations (Retro Classic Grey Theme)
RETRO_BG = (191, 191, 191)       # Classic Windows 95 Grey
RETRO_DARK = (128, 128, 128)     # Dark Gray Shadow
RETRO_LIGHT = (255, 255, 255)    # White Highlight
RETRO_BLUE = (0, 0, 128)         # Classic Title Bar Blue
TEXT_COLOR = (0, 0, 0)           # Pure Black Text

class DetectiveGame:
    def __init__(self):
        try:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("Crime Scene Detective")
        except Exception as e:
            logging.error(f"Failed setting display surface mode: {e}")
            raise
            
        self.clock = pygame.time.Clock()
        self.state = 'MENU'
        self.running = True
        self.sound_enabled = True
        
        self.controller = DetectiveGameController()
        
        self.font_title = pygame.font.SysFont("ms sans serif", 32, bold=True)
        self.font_ui = pygame.font.SysFont("ms sans serif", 16, bold=True)
        self.font_body = pygame.font.SysFont("ms sans serif", 14)
        
        # Path Mapping
        self.src_dir = os.path.join(BASE_DIR, 'src')
        self.gui_dir = os.path.join(self.src_dir, 'RetroWindowsGUI')
        self.portraits_dir = os.path.join(self.src_dir, 'Noir_Men_Portraits')
        self.minigame_output_dir = os.path.join(self.src_dir, 'output')
        
        # Minigame specific render fields
        self.generated_character_surf = None
        self.generated_character_filename = "None Loaded"
        
        self.load_settings()
        self.load_gui_assets()
        self.generate_new_case()

    def load_settings(self):
        path = os.path.join(BASE_DIR, 'data', 'settings.json')
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    self.sound_enabled = json.load(f).get('sound', True)
            except Exception as e:
                logging.warning(f"Could not parse local preferences: {e}")

    def save_settings(self):
        data_dir = os.path.join(BASE_DIR, 'data')
        os.makedirs(data_dir, exist_ok=True)
        try:
            with open(os.path.join(data_dir, 'settings.json'), 'w') as f:
                json.dump({'sound': self.sound_enabled}, f)
        except Exception as e: 
            logging.error(f"Cache save failure: {e}")

    def load_gui_assets(self):
        self.gui_textures = {}
        target_assets = {
            'header': 'Window_Header.png',
            'popup': 'Windows_Example_Popup.png',
            'inner_inverted': 'Windows_Inner_Frame_Inverted.png'
        }
        for key, filename in target_assets.items():
            path = os.path.join(self.gui_dir, filename)
            if os.path.exists(path):
                try:
                    self.gui_textures[key] = pygame.image.load(path).convert_alpha()
                except Exception as e:
                    logging.warning(f"Failed loading GUI asset {filename}: {e}")
                    self.gui_textures[key] = None
            else:
                self.gui_textures[key] = None

    def draw_retro_button(self, rect, text):
        """Renders a standard Windows 95 style button with active real-time mouse press detection"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        
        # Check if mouse is hovering and actively pressing left click over this button
        is_pressed = rect.collidepoint(mouse_pos) and mouse_click[0]
        
        pygame.draw.rect(self.screen, RETRO_BG, rect)
        
        # Real-time reactive shadows
        top_left_color = RETRO_DARK if is_pressed else RETRO_LIGHT
        bottom_right_color = RETRO_LIGHT if is_pressed else RETRO_DARK
        
        pygame.draw.line(self.screen, top_left_color, rect.topleft, rect.topright, 2)
        pygame.draw.line(self.screen, top_left_color, rect.topleft, rect.bottomleft, 2)
        pygame.draw.line(self.screen, bottom_right_color, rect.bottomleft, rect.bottomright, 2)
        pygame.draw.line(self.screen, bottom_right_color, rect.topright, rect.bottomright, 2)
        
        lbl = self.font_ui.render(text, True, TEXT_COLOR)
        text_pos = (rect.centerx - lbl.get_width() // 2, rect.centery - lbl.get_height() // 2)
        
        # Visual mechanical push down offset
        if is_pressed:
            text_pos = (text_pos[0] + 1, text_pos[1] + 1)
            
        self.screen.blit(lbl, text_pos)

    def generate_new_case(self):
        self.current_suspects = []
        available_portraits = []
        if os.path.exists(self.portraits_dir):
            available_portraits = [f for f in os.listdir(self.portraits_dir) if f.lower().endswith('.png')]
        
        for i in range(4):
            if available_portraits:
                img_file = available_portraits[i % len(available_portraits)]
                path = os.path.join(self.portraits_dir, img_file)
                try:
                    surf = pygame.image.load(path).convert_alpha()
                    display_surf = pygame.transform.scale(surf, (140, 140))
                except Exception:
                    display_surf = pygame.Surface((140, 140))
                    display_surf.fill((120, 120, 120))
            else:
                display_surf = pygame.Surface((140, 140))
                display_surf.fill((120, 120, 120))

            trait_combos = [
                ['Dark Jacket', 'Bowtie'], ['Tactical Boots', 'Short Hair'],
                ['Security Badge', 'Tall Posture'], ['White Shirt', 'Dark Hair']
            ]

            self.current_suspects.append({
                'id': i,
                'static_img': display_surf,
                'traits': trait_combos[i % len(trait_combos)],
                'name': f"Suspect #{1007 + i}"
            })
            
        self.guilty_suspect = random.choice(self.current_suspects)
        self.game_result_text = ""
        self.suspect_rects = {}

    def trigger_psd_generator(self):
        """Fires script calculation process, then loads the newest anime asset from the output folder"""
        script_path = os.path.join(self.src_dir, "test_character_generator.py")
        if os.path.exists(script_path):
            try:
                subprocess.run([sys.executable, script_path], cwd=self.src_dir, check=True)
            except Exception as e:
                logging.error(f"Generator calculation subprocess error: {e}")
        
        # Scan for the newly outputted asset inside src/output
        if os.path.exists(self.minigame_output_dir):
            files = [f for f in os.listdir(self.minigame_output_dir) if f.lower().endswith('.png')]
            if files:
                # Target the most recently modified or created image file in src/output
                files.sort(key=lambda x: os.path.getmtime(os.path.join(self.minigame_output_dir, x)))
                latest_filename = files[-1]
                latest_path = os.path.join(self.minigame_output_dir, latest_filename)
                try:
                    raw_surf = pygame.image.load(latest_path).convert_alpha()
                    self.generated_character_surf = pygame.transform.scale(raw_surf, (220, 220))
                    self.generated_character_filename = latest_filename
                except Exception as e:
                    logging.error(f"Failed loading generated preview display: {e}")

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == 'MENU':
                    if self.btn_start.collidepoint(mouse_pos):
                        self.generate_new_case()
                        self.state = 'GAME'
                    elif self.btn_minigame.collidepoint(mouse_pos):
                        # Switch to the dedicated dual box generator interface screen
                        if not self.generated_character_surf:
                            self.trigger_psd_generator()
                        self.state = 'MINIGAME'
                    elif self.btn_settings.collidepoint(mouse_pos): 
                        self.state = 'SETTINGS'
                    elif self.btn_quit.collidepoint(mouse_pos): 
                        self.running = False
                        
                elif self.state == 'MINIGAME':
                    if self.btn_mini_gen.collidepoint(mouse_pos):
                        self.trigger_psd_generator()
                    elif self.btn_mini_back.collidepoint(mouse_pos):
                        self.state = 'MENU'
                        
                elif self.state == 'SETTINGS':
                    if self.btn_audio_toggle.collidepoint(mouse_pos):
                        self.sound_enabled = not self.sound_enabled
                        self.save_settings()
                    elif self.btn_back.collidepoint(mouse_pos): 
                        self.state = 'MENU'
                        
                elif self.state == 'GAME':
                    if self.btn_game_menu.collidepoint(mouse_pos):
                        self.state = 'MENU'
                    elif self.btn_game_exit.collidepoint(mouse_pos):
                        self.running = False
                    
                    for s_id, rect in self.suspect_rects.items():
                        if rect.collidepoint(mouse_pos):
                            if s_id == self.guilty_suspect['id']:
                                self.game_result_text = "CASE SOLVED! You identified the correct suspect."
                            else:
                                self.game_result_text = "CASE LOST! Airtight alibi verified."
                            self.state = 'GAME_OVER'
                elif self.state == 'GAME_OVER':
                    if self.btn_return.collidepoint(mouse_pos): 
                        self.state = 'MENU'

    def draw(self):
        self.screen.fill(RETRO_BG)
        
        if self.state == 'MENU':
            main_window = pygame.Rect(WINDOW_WIDTH//2 - 250, 80, 500, 520)
            pygame.draw.rect(self.screen, RETRO_BG, main_window)
            pygame.draw.rect(self.screen, RETRO_DARK, main_window, 2)
            
            title_bar = pygame.Rect(main_window.x + 4, main_window.y + 4, main_window.width - 8, 30)
            pygame.draw.rect(self.screen, RETRO_BLUE, title_bar)
            t_surf = self.font_ui.render("Crime Scene Detective Console v1.0", True, RETRO_LIGHT)
            self.screen.blit(t_surf, (title_bar.x + 10, title_bar.y + 6))
            
            # Centered buttons now that the side image is removed
            self.btn_start = pygame.Rect(main_window.x + 130, main_window.y + 120, 240, 45)
            self.btn_minigame = pygame.Rect(main_window.x + 130, main_window.y + 190, 240, 45)
            self.btn_settings = pygame.Rect(main_window.x + 130, main_window.y + 260, 240, 45)
            self.btn_quit = pygame.Rect(main_window.x + 130, main_window.y + 330, 240, 45)
            
            self.draw_retro_button(self.btn_start, "START INVESTIGATION")
            self.draw_retro_button(self.btn_minigame, "LAUNCH COMPOSITE GEN")
            self.draw_retro_button(self.btn_settings, "AUDIO CONFIGURATION")
            self.draw_retro_button(self.btn_quit, "EXIT GAME")
            
        elif self.state == 'MINIGAME':
            # Main window wrapper frame
            mini_window = pygame.Rect(WINDOW_WIDTH//2 - 400, 60, 800, 560)
            pygame.draw.rect(self.screen, RETRO_BG, mini_window)
            pygame.draw.rect(self.screen, RETRO_DARK, mini_window, 2)
            
            m_title_bar = pygame.Rect(mini_window.x + 4, mini_window.y + 4, mini_window.width - 8, 30)
            pygame.draw.rect(self.screen, RETRO_BLUE, m_title_bar)
            m_title_surf = self.font_ui.render("Composite Sketch Laboratory Engine", True, RETRO_LIGHT)
            self.screen.blit(m_title_surf, (m_title_bar.x + 10, m_title_bar.y + 6))
            
            # --- BOX 1: COMPOSITE GRAPHIC VISUALIZATION CANVAS ---
            box1_rect = pygame.Rect(mini_window.x + 40, mini_window.y + 60, 340, 380)
            pygame.draw.rect(self.screen, RETRO_BG, box1_rect)
            pygame.draw.rect(self.screen, RETRO_DARK, box1_rect, 2)
            
            box1_bar = pygame.Rect(box1_rect.x + 2, box1_rect.y + 2, box1_rect.width - 4, 24)
            pygame.draw.rect(self.screen, RETRO_DARK, box1_bar)
            b1_lbl = self.font_ui.render("Rendered Output Frame", True, RETRO_LIGHT)
            self.screen.blit(b1_lbl, (box1_bar.x + 8, box1_bar.y + 4))
            
            # Draw real loaded portrait texture inside canvas
            if self.generated_character_surf:
                cx = box1_rect.x + (box1_rect.width - 220) // 2
                cy = box1_rect.y + 50 + (box1_rect.height - 50 - 220) // 2
                self.screen.blit(self.generated_character_surf, (cx, cy))
            else:
                fallback_txt = self.font_body.render("No character file initialized", True, RETRO_DARK)
                self.screen.blit(fallback_txt, (box1_rect.centerx - fallback_txt.get_width()//2, box1_rect.centery))
                
            # --- BOX 2: METADATA & CONTROL TELEMETRY LOG ---
            box2_rect = pygame.Rect(mini_window.x + 420, mini_window.y + 60, 340, 380)
            pygame.draw.rect(self.screen, RETRO_BG, box2_rect)
            pygame.draw.rect(self.screen, RETRO_DARK, box2_rect, 2)
            
            box2_bar = pygame.Rect(box2_rect.x + 2, box2_rect.y + 2, box2_rect.width - 4, 24)
            pygame.draw.rect(self.screen, RETRO_DARK, box2_bar)
            b2_lbl = self.font_ui.render("Asset Core Manifest Data", True, RETRO_LIGHT)
            self.screen.blit(b2_lbl, (box2_bar.x + 8, box2_bar.y + 4))
            
            # Print asset structural properties inside context block
            meta_y = box2_rect.y + 40
            properties = [
                f"Target Engine: Pygame Surface API",
                f"Source File: {self.generated_character_filename}",
                f"Texture Matrix Bounds: 220x220 scaled",
                f"Format Context: RGB Alpha Layered",
                f"Environment Status: Valid Ready"
            ]
            for prop in properties:
                p_surf = self.font_body.render(f">> {prop}", True, TEXT_COLOR)
                self.screen.blit(p_surf, (box2_rect.x + 15, meta_y))
                meta_y += 30
            
            # Action Execution Panel
            self.btn_mini_gen = pygame.Rect(mini_window.x + 80, mini_window.y + 475, 280, 45)
            self.btn_mini_back = pygame.Rect(mini_window.x + 440, mini_window.y + 475, 280, 45)
            
            self.draw_retro_button(self.btn_mini_gen, "REGENERATE CHARACTER Sketch")
            self.draw_retro_button(self.btn_mini_back, "RETURN TO MAIN WINDOW")
            
        elif self.state == 'SETTINGS':
            setting_box = pygame.Rect(WINDOW_WIDTH//2 - 200, 150, 400, 300)
            pygame.draw.rect(self.screen, RETRO_BG, setting_box)
            pygame.draw.rect(self.screen, RETRO_DARK, setting_box, 2)
            
            s_bar = pygame.Rect(setting_box.x + 4, setting_box.y + 4, setting_box.width - 8, 30)
            pygame.draw.rect(self.screen, RETRO_BLUE, s_bar)
            s_surf = self.font_ui.render("Options Menu", True, RETRO_LIGHT)
            self.screen.blit(s_surf, (s_bar.x + 10, s_bar.y + 6))
            
            self.btn_audio_toggle = pygame.Rect(setting_box.x + 50, setting_box.y + 100, 300, 45)
            self.btn_back = pygame.Rect(setting_box.x + 100, setting_box.y + 180, 200, 45)
            
            self.draw_retro_button(self.btn_audio_toggle, f"AUDIO STATE: {'ACTIVE' if self.sound_enabled else 'MUTED'}")
            self.draw_retro_button(self.btn_back, "RETURN TO MENU")
            
        elif self.state == 'GAME':
            header_rect = pygame.Rect(30, 30, WINDOW_WIDTH - 60, 100)
            pygame.draw.rect(self.screen, RETRO_BG, header_rect)
            pygame.draw.rect(self.screen, RETRO_DARK, header_rect, 2)
            
            clue_title = self.font_ui.render("CASE BRIEF - ACTIVE LEADS:", True, TEXT_COLOR)
            self.screen.blit(clue_title, (header_rect.x + 20, header_rect.y + 15))
            
            clue_str = f"Evidence points to suspect matching characteristics: {', '.join(self.guilty_suspect['traits'])}"
            clue_txt = self.font_body.render(clue_str, True, RETRO_BLUE)
            self.screen.blit(clue_txt, (header_rect.x + 20, header_rect.y + 45))
            
            card_w, card_h = 220, 380
            start_x = (WINDOW_WIDTH - ((4 * card_w) + (3 * 20))) // 2
            
            for i, sus in enumerate(self.current_suspects):
                cx = start_x + (i * (card_w + 20))
                cy = 160
                c_rect = pygame.Rect(cx, cy, card_w, card_h)
                
                pygame.draw.rect(self.screen, RETRO_BG, c_rect)
                pygame.draw.rect(self.screen, RETRO_DARK, c_rect, 2)
                self.suspect_rects[sus['id']] = c_rect
                
                self.screen.blit(sus['static_img'], (cx + (card_w - 140)//2, cy + 20))
                
                n_surf = self.font_ui.render(sus['name'], True, TEXT_COLOR)
                self.screen.blit(n_surf, (c_rect.centerx - n_surf.get_width()//2, cy + 180))
                
                desc_y = cy + 210
                for trait in sus['traits']:
                    t_lbl = self.font_body.render(f"• {trait}", True, TEXT_COLOR)
                    self.screen.blit(t_lbl, (cx + 20, desc_y))
                    desc_y += 25

            footer_rect = pygame.Rect(30, WINDOW_HEIGHT - 75, WINDOW_WIDTH - 60, 60)
            pygame.draw.rect(self.screen, RETRO_BG, footer_rect)
            pygame.draw.rect(self.screen, RETRO_DARK, footer_rect, 2)

            self.btn_game_menu = pygame.Rect(footer_rect.x + 20, footer_rect.y + 10, 220, 40)
            self.btn_game_exit = pygame.Rect(footer_rect.x + footer_rect.width - 240, footer_rect.y + 10, 220, 40)
            
            self.draw_retro_button(self.btn_game_menu, "RETURN TO MENU")
            self.draw_retro_button(self.btn_game_exit, "EXIT GAME")
                    
        elif self.state == 'GAME_OVER':
            end_window = pygame.Rect(WINDOW_WIDTH//2 - 200, 200, 400, 220)
            pygame.draw.rect(self.screen, RETRO_BG, end_window)
            pygame.draw.rect(self.screen, RETRO_DARK, end_window, 2)
            
            r_bar = pygame.Rect(end_window.x + 4, end_window.y + 4, end_window.width - 8, 30)
            pygame.draw.rect(self.screen, RETRO_BLUE, r_bar)
            
            res_title = self.font_ui.render("Investigation Complete", True, RETRO_LIGHT)
            self.screen.blit(res_title, (r_bar.x + 10, r_bar.y + 6))
            
            res_surf = self.font_body.render(self.game_result_text, True, TEXT_COLOR)
            self.screen.blit(res_surf, (end_window.centerx - res_surf.get_width()//2, end_window.y + 70))
            
            self.btn_return = pygame.Rect(end_window.x + 100, end_window.y + 120, 200, 45)
            self.draw_retro_button(self.btn_return, "RETURN TO MENU")

    def run(self):
        try:
            while self.running:
                self.handle_events()
                self.draw()
                pygame.display.flip()
                self.clock.tick(FPS)
        except Exception as game_err:
            logging.critical(f"UNHANDLED RUNTIME FAULT DETECTED: {game_err}")
        finally:
            pygame.quit()

if __name__ == "__main__":
    game = DetectiveGame()
    game.run()