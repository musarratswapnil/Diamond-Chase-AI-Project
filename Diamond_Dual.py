import pygame
import pygame.gfxdraw
import button
import copy
import time
import random
import math
from ai_algorithms import AStarFuzzyAI
pygame.init()

screen_info = pygame.display.Info()
width = screen_info.current_w
height = screen_info.current_h
try:
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.SCALED)
except pygame.error:
    # Fallback for environments that don't support SCALED with explicit size
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
pygame.display.set_caption("Diamond Chase - Modern")

# Modern color palette
COLOR_BG = (15, 20, 40)
COLOR_PRIMARY = (100, 200, 255)
COLOR_SECONDARY = (150, 100, 255)
COLOR_AI = (255, 80, 80)
COLOR_HUMAN = (80, 255, 150)
COLOR_ACCENT = (255, 200, 100)
COLOR_OPTION = (196, 215, 255)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = COLOR_AI
GREEN = COLOR_HUMAN
OPTION_COLOR = COLOR_OPTION

# Modern UI Components
class ModernUI:
    @staticmethod
    def draw_glassmorphic_panel(surface, rect, color, alpha=180):
        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*color, alpha), panel_surface.get_rect(), border_radius=20)
        
        for i in range(rect.height // 3):
            highlight_alpha = int(50 * (1 - i / (rect.height // 3)))
            pygame.draw.line(panel_surface, (255, 255, 255, highlight_alpha), 
                           (10, i), (rect.width - 10, i))
        
        pygame.draw.rect(panel_surface, (255, 255, 255, 80), panel_surface.get_rect(), 
                        width=2, border_radius=20)
        surface.blit(panel_surface, rect.topleft)
    
    @staticmethod
    def draw_glowing_text(surface, text, font, color, pos, glow_intensity=1):
        for i in range(min(glow_intensity, 2), 0, -1):
            glow_alpha = max(20, 60 // (i + 1))
            glow_surface = font.render(text, True, (*color[:3], glow_alpha))
            glow_rect = glow_surface.get_rect(center=pos)
            for offset_x in range(-i, i+1):
                for offset_y in range(-i, i+1):
                    if offset_x*offset_x + offset_y*offset_y <= i*i:
                        surface.blit(glow_surface, (glow_rect.x + offset_x, glow_rect.y + offset_y))
        text_surface = font.render(text, True, (*color[:3], 230))
        text_rect = text_surface.get_rect(center=pos)
        surface.blit(text_surface, text_rect)
    
    @staticmethod
    def draw_glowing_circle(surface, color, center, radius, glow_layers=2):
        for i in range(glow_layers, 0, -1):
            alpha = max(20, 90 // (i + 1))
            glow_radius = radius + i * 2
            glow_surface = pygame.Surface((glow_radius * 2 + 2, glow_radius * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*color[:3], alpha), (glow_radius + 1, glow_radius + 1), glow_radius)
            surface.blit(glow_surface, (center[0] - glow_radius - 1, center[1] - glow_radius - 1))
        pygame.draw.circle(surface, (*color[:3], 220), center, radius)
    
    @staticmethod
    def draw_glowing_line(surface, color, start, end, width=2, glow_layers=0):
        pygame.draw.line(surface, (*color[:3], 200), start, end, width)
    
    @staticmethod
    def draw_glowing_polygon(surface, color, points, width=2, glow_layers=0):
        pygame.draw.polygon(surface, (*color[:3], 180), points, width)
    
    @staticmethod
    def draw_futuristic_background(surface, time_offset=0):
        for y in range(height):
            progress = y / height
            r = int(18 + 6 * math.sin(progress * 1.2 + time_offset * 0.0006))
            g = int(22 + 8 * math.sin(progress * 1.5 + time_offset * 0.0007))
            b = int(34 + 10 * math.sin(progress * 1.8 + time_offset * 0.0008))
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))


class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def emit(self, pos, color, count=16, velocity_range=3):
        for _ in range(min(count, 20)):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.6, velocity_range)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            
            self.particles.append({
                'pos': list(pos),
                'velocity': velocity,
                'color': color,
                'lifetime': random.randint(24, 48),
                'max_lifetime': 48,
                'size': random.randint(2, 4)
            })
    
    def update(self):
        for particle in self.particles[:]:
            particle['pos'][0] += particle['velocity'][0]
            particle['pos'][1] += particle['velocity'][1]
            particle['velocity'][1] += 0.12
            particle['lifetime'] -= 1
            if particle.get('shape') == 'confetti':
                particle['rotation'] = particle.get('rotation', 0.0) + particle.get('rot_speed', 0.0)
                particle['spark_timer'] = particle.get('spark_timer', 0) - 1
                if particle['spark_timer'] <= 0:
                    particle['spark_timer'] = 3
                    self.particles.append({
                        'pos': [particle['pos'][0], particle['pos'][1]],
                        'velocity': [random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)],
                        'color': (255, 255, 255),
                        'lifetime': 18,
                        'max_lifetime': 18,
                        'size': 2
                    })
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        for particle in self.particles:
            alpha = min(255, int(255 * (particle['lifetime'] / particle['max_lifetime'])))
            color = (*particle['color'][:3], alpha)
            size = max(1, int(particle['size'] * (particle['lifetime'] / particle['max_lifetime'])))
            if particle.get('shape') == 'confetti':
                s = max(2, size)
                surf = pygame.Surface((s * 2, s), pygame.SRCALPHA)
                pygame.draw.rect(surf, color, pygame.Rect(0, 0, s * 2, s), border_radius=2)
                rot = particle.get('rotation', 0.0)
                rs = pygame.transform.rotate(surf, rot)
                surface.blit(rs, (int(particle['pos'][0]), int(particle['pos'][1])))
            else:
                particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, color, (size, size), size)
                surface.blit(particle_surface, (int(particle['pos'][0] - size), int(particle['pos'][1] - size)))

    def emit_confetti(self, pos, base_color, count=24):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            def jitter(c):
                return max(0, min(255, int(c + random.uniform(-80, 80))))
            color = (jitter(base_color[0]), jitter(base_color[1]), jitter(base_color[2]))
            self.particles.append({
                'pos': [pos[0], pos[1]],
                'velocity': velocity,
                'color': color,
                'lifetime': random.randint(30, 60),
                'max_lifetime': 60,
                'size': random.randint(2, 4),
                'shape': 'confetti',
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-10, 10),
                'spark_timer': random.randint(0, 3)
            })


class FloatingTextSystem:
    def __init__(self):
        self.items = []  # each: {text,pos,vel,color,life,max}
        self.font = pygame.font.SysFont("Segoe UI Black", 28)
    
    def spawn(self, text, pos, color):
        self.items.append({
            'text': text,
            'pos': [pos[0], pos[1]],
            'vel': [0, -0.8],
            'color': color,
            'life': 60,
            'max': 60
        })
    
    def update(self):
        for it in self.items[:]:
            it['pos'][0] += it['vel'][0]
            it['pos'][1] += it['vel'][1]
            it['life'] -= 1
            if it['life'] <= 0:
                self.items.remove(it)
    
    def draw(self, surface):
        for it in self.items:
            alpha = int(255 * (it['life'] / it['max']))
            color = (*it['color'][:3], alpha)
            surf = self.font.render(it['text'], True, color)
            shadow = self.font.render(it['text'], True, (0,0,0))
            rect = surf.get_rect(center=(int(it['pos'][0]), int(it['pos'][1])))
            surface.blit(shadow, (rect.x+2, rect.y+2))
            surface.blit(surf, rect)

class ModernButton:
    def __init__(self, x, y, width, height, text, font, base_color, hover_color, text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = list(base_color)
        self.clicked = False
        self.hover_scale = 1.0
        self.target_scale = 1.0
        self.ripple = None  # {'pos':(x,y), 'radius':0, 'alpha':180}
    
    def update(self, mouse_pos, mouse_pressed):
        action = False
        
        if self.rect.collidepoint(mouse_pos):
            self.target_scale = 1.05
            for i in range(3):
                self.current_color[i] += (self.hover_color[i] - self.current_color[i]) * 0.1
            
            if mouse_pressed and not self.clicked:
                self.clicked = True
                action = True
                # start ripple
                self.ripple = {'pos': mouse_pos, 'radius': 0, 'alpha': 180}
        else:
            self.target_scale = 1.0
            for i in range(3):
                self.current_color[i] += (self.base_color[i] - self.current_color[i]) * 0.1
        
        if not mouse_pressed:
            self.clicked = False
        
        self.hover_scale += (self.target_scale - self.hover_scale) * 0.2
        return action
    
    def draw(self, surface):
        scaled_width = int(self.rect.width * self.hover_scale)
        scaled_height = int(self.rect.height * self.hover_scale)
        scaled_rect = pygame.Rect(
            self.rect.centerx - scaled_width // 2,
            self.rect.centery - scaled_height // 2,
            scaled_width, scaled_height
        )
        
        color_tuple = tuple(int(c) for c in self.current_color)
        ModernUI.draw_glassmorphic_panel(surface, scaled_rect, color_tuple, alpha=180)
        
        for i in range(3, 0, -1):
            alpha = min(255, 100 // i)
            border_surface = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(border_surface, (*color_tuple, alpha), border_surface.get_rect(), 
                           width=i, border_radius=20)
            surface.blit(border_surface, scaled_rect.topleft)
        
        # Draw button text like score numbers: solid with subtle shadow
        text_surface = self.font.render(self.text, True, self.text_color)
        shadow_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        surface.blit(shadow_surface, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text_surface, text_rect)
        # Draw ripple
        if self.ripple:
            self.ripple['radius'] += 12
            self.ripple['alpha'] = max(0, self.ripple['alpha'] - 12)
            rx, ry = self.ripple['pos']
            rr = self.ripple['radius']
            ripple_surf = pygame.Surface((rr*2, rr*2), pygame.SRCALPHA)
            pygame.draw.circle(ripple_surf, (*self.text_color[:3], self.ripple['alpha']), (rr, rr), rr, width=4)
            surface.blit(ripple_surf, (rx-rr, ry-rr))
            if self.ripple['alpha'] == 0:
                self.ripple = None


class ImageButton:
    def __init__(self, x, y, image, scale, glow_color, label=None, label_font=None, label_color=(255, 255, 255)):
        self.original_image = pygame.transform.scale(
            image, 
            (int(image.get_width() * scale), int(image.get_height() * scale))
        )
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.glow_color = glow_color
        self.clicked = False
        self.hover_scale = 1.0
        self.target_scale = 1.0
        self.base_x = x
        self.base_y = y
        self.circle_image = None
        self.label = label
        self.label_font = label_font
        self.label_color = label_color

    def _make_circular(self, surf):
        size = max(surf.get_width(), surf.get_height())
        square = pygame.Surface((size, size), pygame.SRCALPHA)
        # center the image on a square surface
        offset_x = (size - surf.get_width()) // 2
        offset_y = (size - surf.get_height()) // 2
        square.blit(surf, (offset_x, offset_y))
        mask = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (size // 2, size // 2), size // 2)
        circ = square.copy()
        circ.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return circ
    
    def update(self, mouse_pos, mouse_pressed):
        action = False
        
        if self.rect.collidepoint(mouse_pos):
            self.target_scale = 1.1
            if mouse_pressed and not self.clicked:
                self.clicked = True
                action = True
        else:
            self.target_scale = 1.0
        
        if not mouse_pressed:
            self.clicked = False
        
        self.hover_scale += (self.target_scale - self.hover_scale) * 0.2
        
        new_width = int(self.original_image.get_width() * self.hover_scale)
        new_height = int(self.original_image.get_height() * self.hover_scale)
        self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
        self.rect = self.image.get_rect(center=(self.base_x, self.base_y))
        self.circle_image = self._make_circular(self.image)
        
        return action
    
    def draw(self, surface):
        glow_radius = max(self.rect.width, self.rect.height) // 2 + 10
        for i in range(5, 0, -1):
            alpha = min(255, 80 // i)
            glow_color = (*self.glow_color[:3], alpha)
            radius = int(glow_radius + i * 5)
            
            glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (radius, radius), radius)
            surface.blit(glow_surface, (self.rect.centerx - radius, self.rect.centery - radius))
        
        if self.circle_image is None:
            self.circle_image = self._make_circular(self.image)
        circ_rect = self.circle_image.get_rect(center=self.rect.center)
        surface.blit(self.circle_image, circ_rect)
        # optional centered label overlay
        if self.label and self.label_font:
            text_surface = self.label_font.render(self.label, True, self.label_color)
            text_rect = text_surface.get_rect(center=circ_rect.center)
            # simple thin outline like before
            outline = [(1,0),(-1,0),(0,1),(0,-1)]
            for dx, dy in outline:
                shadow = self.label_font.render(self.label, True, (0,0,0))
                surface.blit(shadow, (text_rect.x+dx, text_rect.y+dy))
            surface.blit(text_surface, text_rect)


class MinimalButton:
    def __init__(self, x, y, width, height, text, font, color, hover_fill=None, icon_type=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_fill = hover_fill if hover_fill else color
        self.icon_type = icon_type  # 'back' | 'restart' | None
        self.clicked = False
        self.hover_t = 0.0
        self.target_hover = 0.0
    
    def update(self, mouse_pos, mouse_pressed):
        action = False
        if self.rect.collidepoint(mouse_pos):
            self.target_hover = 1.0
            if mouse_pressed and not self.clicked:
                self.clicked = True
                action = True
        else:
            self.target_hover = 0.0
        if not mouse_pressed:
            self.clicked = False
        self.hover_t += (self.target_hover - self.hover_t) * 0.2
        return action
    
    def draw(self, surface):
        radius = self.rect.height // 2
        t = self.hover_t
        # soft drop shadow
        shadow = pygame.Surface((self.rect.width+20, self.rect.height+20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, int(70+70*t)), shadow.get_rect())
        surface.blit(shadow, (self.rect.x-10, self.rect.y+self.rect.height-8))
        # animated gradient fill
        grad = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        for i in range(self.rect.height):
            s = i / max(1, self.rect.height-1)
            r = int(self.hover_fill[0]*(0.7+0.3*s))
            g = int(self.hover_fill[1]*(0.7+0.3*s))
            b = int(self.hover_fill[2]*(0.7+0.3*s))
            a = int(90 + 120*t)
            pygame.draw.line(grad, (r, g, b, a), (0, i), (self.rect.width, i))
        pygame.draw.rect(grad, (255,255,255,int(40+40*t)), grad.get_rect(), border_radius=radius)
        surface.blit(grad, self.rect)
        # inner highlight
        highlight = pygame.Rect(self.rect.x+6, self.rect.y+6, self.rect.width-12, (self.rect.height-12)//2)
        pygame.draw.rect(surface, (255,255,255,int(35+40*t)), highlight, border_radius=radius//2)
        # glowing outline
        pygame.draw.rect(surface, (*self.color, 220), self.rect, width=2, border_radius=radius)
        if t > 0.01:
            pygame.draw.rect(surface, (*self.color, int(120*t)), self.rect.inflate(8,8), width=2, border_radius=radius+4)
        # optional icon
        content_left = self.rect.x + 18
        if self.icon_type == 'back':
            # chevron
            p1 = (content_left+8, self.rect.centery)
            p2 = (content_left+22, self.rect.centery-12)
            p3 = (content_left+22, self.rect.centery+12)
            pygame.draw.polygon(surface, (240,245,250), [p1,p2,p3])
            content_left += 26
        elif self.icon_type == 'restart':
            # circular arrow
            center = (content_left+14, self.rect.centery)
            pygame.draw.circle(surface, (240,245,250), center, 10, width=3)
            pygame.draw.polygon(surface, (240,245,250), [(center[0]+10, center[1]-2),(center[0]+16, center[1]-2),(center[0]+13, center[1]-8)])
            content_left += 30
        # text
        txt = self.font.render(self.text, True, (240, 245, 250))
        txt_rect = txt.get_rect()
        available = self.rect.width - (content_left - self.rect.x) - 14
        pos_x = content_left + max(0, (available - txt_rect.width)//2)
        surface.blit(txt, (pos_x, self.rect.centery - txt_rect.height//2))


class PillButton:
    def __init__(self, x, y, width, height, text, font, left_icon=None,
                 base_color=(70, 110, 200), hover_color=(90, 140, 255), text_color=(245, 248, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.left_icon = left_icon
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hover_t = 0.0
        self.clicked = False
        self.target_hover = 0.0
    
    def _draw_gradient(self, surface, rect, c1, c2, radius=28):
        grad_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for i in range(rect.height):
            t = i / max(1, rect.height - 1)
            r = int(c1[0] * (1 - t) + c2[0] * t)
            g = int(c1[1] * (1 - t) + c2[1] * t)
            b = int(c1[2] * (1 - t) + c2[2] * t)
            pygame.draw.line(grad_surf, (r, g, b, 230), (0, i), (rect.width, i))
        pygame.draw.rect(grad_surf, (255, 255, 255, 28), grad_surf.get_rect(), border_radius=radius, width=1)
        surface.blit(grad_surf, rect)
    
    def update(self, mouse_pos, mouse_pressed):
        action = False
        if self.rect.collidepoint(mouse_pos):
            self.target_hover = 1.0
            if mouse_pressed and not self.clicked:
                self.clicked = True
                action = True
        else:
            self.target_hover = 0.0
        if not mouse_pressed:
            self.clicked = False
        self.hover_t += (self.target_hover - self.hover_t) * 0.18
        return action
    
    def draw(self, surface):
        # shadow
        shadow_alpha = int(40 + 40 * self.hover_t)
        shadow_rect = self.rect.move(0, 6)
        pygame.draw.ellipse(surface, (0, 0, 0, shadow_alpha), shadow_rect)
        # gradient background
        mix = lambda a, b, t: (int(a[0]*(1-t)+b[0]*t), int(a[1]*(1-t)+b[1]*t), int(a[2]*(1-t)+b[2]*t))
        color_top = mix(self.base_color, self.hover_color, self.hover_t)
        color_bottom = mix((max(0, self.base_color[0]-20), max(0, self.base_color[1]-20), max(0, self.base_color[2]-20)),
                           (max(0, self.hover_color[0]-20), max(0, self.hover_color[1]-20), max(0, self.hover_color[2]-20)),
                           self.hover_t)
        rounded_rect = pygame.Rect(self.rect)
        self._draw_gradient(surface, rounded_rect, color_top, color_bottom, radius=32)
        # content
        cx, cy = self.rect.center
        text_surface = self.font.render(self.text, True, (*self.text_color, 240))
        content_width = text_surface.get_width()
        icon_offset = 0
        if self.left_icon:
            icon_h = int(self.rect.height * 0.52)
            scale = icon_h / self.left_icon.get_height()
            icon_w = int(self.left_icon.get_width() * scale)
            icon_img = pygame.transform.smoothscale(self.left_icon, (icon_w, icon_h))
            icon_x = self.rect.x + 22
            icon_y = self.rect.centery - icon_h // 2
            surface.blit(icon_img, (icon_x, icon_y))
            icon_offset = icon_w + 16
        text_x = self.rect.x + 22 + icon_offset
        text_y = cy - text_surface.get_height() // 2
        surface.blit(text_surface, (text_x, text_y))

class DiamondAnimation:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.rotation = 0
        self.pulse_scale = 1.0
    
    def update(self):
        self.rotation += 0.02
        self.pulse_scale = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() * 0.003)
    
    def draw(self, surface):
        points = []
        for i in range(4):
            angle = self.rotation + (i * 2 * math.pi / 4)
            x = self.x + math.cos(angle) * self.size * self.pulse_scale
            y = self.y + math.sin(angle) * self.size * self.pulse_scale
            points.append((x, y))
        
        for i in range(3, 0, -1):
            alpha = min(255, 150 // i)
            offset_points = [(p[0] + i * 2, p[1] + i * 2) for p in points]
            
            glow_surface = pygame.Surface((int(self.size * 4), int(self.size * 4)), pygame.SRCALPHA)
            adjusted_points = [(p[0] - self.x + self.size * 2, p[1] - self.y + self.size * 2) 
                             for p in offset_points]
            pygame.draw.polygon(glow_surface, (100, 200, 255, alpha), adjusted_points)
            surface.blit(glow_surface, (self.x - self.size * 2, self.y - self.size * 2))
        
        pygame.draw.polygon(surface, (100, 200, 255), points)
        pygame.draw.polygon(surface, (150, 220, 255), points, 3)


def draw_winner_banner(surface, text, color, center_y, time_ms):
    # Animated banner with scale pulse, shadow, underline glow, and color sweep
    pulse = 1.0 + 0.05 * math.sin(time_ms * 0.005)
    base_font = pygame.font.SysFont("Segoe UI Black", int(74 * pulse))
    # Create gradient sweep
    text_mask = base_font.render(text, True, (255, 255, 255))
    w, h = text_mask.get_size()
    gradient = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(w):
        hue = (x + (time_ms//8)) % w
        t = hue / w
        r = int(255 * (0.5 + 0.5 * math.sin(2*math.pi*(t))))
        g = int(255 * (0.5 + 0.5 * math.sin(2*math.pi*(t + 1/3))))
        b = int(255 * (0.5 + 0.5 * math.sin(2*math.pi*(t + 2/3))))
        pygame.draw.line(gradient, (r, g, b, 230), (x, 0), (x, h))
    colored_text = gradient.copy()
    colored_text.blit(text_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    outline_surface = base_font.render(text, True, (0, 0, 0))
    # Position centered
    target_rect = colored_text.get_rect(center=(width // 2, center_y))
    # Multi-shadow for depth
    for ox, oy, a in [(3,3,160),(1,1,90)]:
        shadow = outline_surface.copy()
        shadow.set_alpha(a)
        surface.blit(shadow, (target_rect.x + ox, target_rect.y + oy))
    # Soft color glow behind
    glow = pygame.Surface((target_rect.width + 120, target_rect.height + 80), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (*color, 70), glow.get_rect())
    surface.blit(glow, (target_rect.x - 60, target_rect.y - 40))
    # Main gradient text
    surface.blit(colored_text, target_rect)
    # Underline highlight
    underline_w = target_rect.width
    underline_h = 10
    underline_rect = pygame.Rect(0, 0, underline_w, underline_h)
    underline_rect.center = (width // 2, target_rect.bottom + 14)
    pygame.draw.rect(surface, (*color, 220), underline_rect, border_radius=6)

def draw_score_panel(surface, text, score, pos, color, pulse_time):
    panel_width = 280
    panel_height = 100
    panel_rect = pygame.Rect(pos[0], pos[1], panel_width, panel_height)
    
    pulse = 1.0 + 0.05 * math.sin(pulse_time * 0.003)
    
    ModernUI.draw_glassmorphic_panel(surface, panel_rect, color, alpha=200)
    
    text_y = panel_rect.centery - 20
    font_score = pygame.font.SysFont("Segoe UI Black", 30)
    # render label like the number (solid with subtle shadow)
    label_surface = font_score.render(text, True, (255, 255, 255))
    label_shadow = font_score.render(text, True, (0, 0, 0))
    label_target = label_surface.get_rect(center=(panel_rect.centerx, text_y))
    surface.blit(label_shadow, (label_target.x + 2, label_target.y + 2))
    surface.blit(label_surface, label_target)
    
    score_y = panel_rect.centery + 20
    score_font = pygame.font.SysFont("Segoe UI Black", int(64 * pulse))
    # render bright white score with subtle shadow for readability
    score_surface = score_font.render(str(score), True, (255, 255, 255))
    shadow_surface = score_font.render(str(score), True, (0, 0, 0))
    target = score_surface.get_rect(center=(panel_rect.centerx, score_y))
    surface.blit(shadow_surface, (target.x + 2, target.y + 2))
    surface.blit(score_surface, target)


center_x = width // 2
center_y = height // 2 + 70

bigger_side = width // 2.5
rhombus_width = 140
rhombus_height = 140
rhombus_thickness = 3

top = (center_x, center_y - bigger_side // 2)
top_l = (top[0] + rhombus_width // 2, top[1] + rhombus_height // 2)
top_r = (top[0] - rhombus_width // 2, top[1] + rhombus_height // 2)
top_t = (top[0], top[1] + rhombus_height)

right = (center_x + bigger_side // 2, center_y)
right_r = (right[0] - rhombus_width // 2, right[1] - rhombus_height // 2)
right_l = (right[0] - rhombus_height // 2, right[1] + rhombus_height // 2)
right_t = (right[0] - rhombus_height, right[1])

left = (center_x - bigger_side // 2, center_y)
left_r = (left[0] + rhombus_height // 2, left[1] + rhombus_width // 2)
left_l = (left[0] + rhombus_height // 2, left[1] - rhombus_width // 2)
left_t = (left[0] + rhombus_height, left[1])

bottom = (center_x, center_y + bigger_side // 2)
bottom_r = (bottom[0] + rhombus_height // 2, bottom[1] - rhombus_height // 2)
bottom_l = (bottom[0] - rhombus_height // 2, bottom[1] - rhombus_height // 2)
bottom_t = (bottom[0], bottom[1] - rhombus_height)

center = (center_x, center_y)
center_l = (center[0] - rhombus_height // 2, center[1])
center_r = (center[0] + rhombus_height // 2, center[1])
center_t_up = (center[0], center[1] - rhombus_height // 2)
center_t_down = (center[0], center[1] + rhombus_height // 2)

ai_beads_position = [top, top_l, top_r, top_t, left_l, right_r]
human_beads_position = [bottom, bottom_l, bottom_r, bottom_t, left_r, right_l]


def Get_First_Hop_Neighbour():
    Neighbour = {
        top: (top_l, top_r, top_t),
        top_r: (top, top_t, left_l),
        top_l: (top, top_t, right_r),
        top_t: (top, top_l, top_r, center_t_up),
        left: (left_l, left_r, left_t),
        left_l: (left, left_t, top_r),
        left_r: (left, left_t, bottom_l),
        left_t: (left, left_l, left_r, center_l),
        right: (right_r, right_l, right_t),
        right_r: (right, right_t, top_l),
        right_l: (right, right_t, bottom_r),
        right_t: (right_r, right_l, right, center_r),
        bottom: (bottom_l, bottom_r, bottom_t),
        bottom_r: (bottom, bottom_t, right_l),
        bottom_l: (bottom, bottom_t, left_r),
        bottom_t: (bottom, bottom_l, bottom_r, center_t_down),
        center: (center_l, center_r, center_t_up, center_t_down),
        center_l: (center, center_t_up, center_t_down, left_t),
        center_r: (center, center_t_down, center_t_up, right_t),
        center_t_up: (center, center_l, center_r, top_t),
        center_t_down: (center, center_l, center_r, bottom_t)
    }
    return Neighbour


neighbour = Get_First_Hop_Neighbour()

text_font = pygame.font.SysFont("Calibri", 24)
text_font_won = pygame.font.SysFont("Bahnschrift SemiBold", 40)
font = pygame.font.SysFont("Bahnschrift", 80)
menu_font = pygame.font.SysFont("Calibri", 28)
button_font = pygame.font.SysFont("Bahnschrift SemiBold", 24)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_centered_text_below(text, font, color, rect, margin):
    img = font.render(text, True, color)
    text_rect = img.get_rect()
    text_rect.midtop = (rect.centerx, rect.bottom + margin)
    screen.blit(img, text_rect)


def Draw_Circle(ara, color):
    for item in ara:
        ModernUI.draw_glowing_circle(screen, color, item, 10, glow_layers=5)


def Find_Match(ara, pos):
    for item in ara:
        x = item[0]
        y = item[1]
        if abs(x - pos[0]) <= 40 and abs(y - pos[1]) <= 40:
            return x, y
    return -1, -1


def Heuristic_Val(pos, neighbour, ai_beads, human_beads):
    ara = neighbour[pos]
    count = len(ara)
    
    for item in ara:
        x, y = Find_Match(ai_beads, item)
        if x != -1:
            count -= 1
            continue
        x, y = Find_Match(human_beads, item)
        if x != -1:
            count -= 1
    
    return count


def Check_Winner(ai_beads_position, human_beads_position):
    if len(ai_beads_position) < 4:
        return 0
    elif len(human_beads_position) < 4:
        return 1
    else:
        return -1


def Trap_Beads(x, y, neighbour, color, ai_beads, human_beads):
    ara = neighbour[(x, y)]
    count = len(ara)
    count2 = 0
    
    for item in ara:
        x, y = Find_Match(ai_beads, item)
        if x != -1:
            count -= 1
            if color == GREEN:
                count2 += 1
                continue
        
        x, y = Find_Match(human_beads, item)
        if x != -1:
            count -= 1
            if color == RED:
                count2 += 1
                continue
    return count, count2


def Draw_Polygon():
    ModernUI.draw_glowing_polygon(screen, COLOR_PRIMARY, [top, right, bottom, left], width=3)
    ModernUI.draw_glowing_polygon(screen, COLOR_PRIMARY, [center_t_up, center_r, center_t_down, center_l], width=3)
    ModernUI.draw_glowing_polygon(screen, COLOR_PRIMARY, [top, top_l, top_t, top_r], width=3)
    ModernUI.draw_glowing_polygon(screen, COLOR_PRIMARY, [right_l, right, right_r, right_t], width=3)
    ModernUI.draw_glowing_polygon(screen, COLOR_PRIMARY, [bottom_r, bottom_t, bottom_l, bottom], width=3)
    ModernUI.draw_glowing_polygon(screen, COLOR_PRIMARY, [left_l, left_t, left_r, left], width=3)


def Heuristic_Value_Min_Max(pos, ara_ai, ara_human):
    ara = neighbour[pos]
    count = len(ara)
    for item in ara:
        x, y = Find_Match(ara_ai, item)
        p, q = Find_Match(ara_human, item)
        if x != -1 or p != -1:
            count -= 1
    return count


def Empty_Neighbour(node, ai_beads, human_beads):
    ara = neighbour[node]
    ara1 = []
    
    for item in ara:
        x, y = Find_Match(ai_beads, item)
        if x != -1:
            continue
        x, y = Find_Match(human_beads, item)
        if x != -1:
            continue
        ara1.append(item)
    
    return ara1


def All_Heuristic_Value_Min_Max_Ai(ara_ai, ara_human):
    result = []
    for item in ara_ai:
        x = Heuristic_Value_Min_Max(item, ara_ai, ara_human)
        result.append(x)
    return result


def All_Heuristic_Value_Min_Max_Human(ara_ai, ara_human):
    result = []
    for item in ara_human:
        x = Heuristic_Value_Min_Max(item, ara_ai, ara_human)
        result.append(x)
    return result

def _mini_max_ab(ara_ai, ara_human, depth, maxPlayer, alpha, beta):
    best_item = None
    best_node = None

    # Leaf evaluation
    if depth == 0:
        result1 = All_Heuristic_Value_Min_Max_Ai(ara_ai, ara_human)
        result2 = All_Heuristic_Value_Min_Max_Human(ara_ai, ara_human)
        return (sum(result1) - sum(result2)) + len(ara_ai) - len(ara_human), best_item, best_node

    if maxPlayer:
        maxEle = -math.inf
        best_item = None
        best_node = None
        for node in ara_ai:
            val = Heuristic_Val(node, neighbour, ara_ai, ara_human)
            if val == 0:
                continue
            else:
                ara = Empty_Neighbour(node, ara_ai, ara_human)
                for item in ara:
                    temp_ai = copy.deepcopy(ara_ai)
                    x, y = Find_Match(temp_ai, item)
                    p, q = Find_Match(ara_human, item)
                    if x != -1 or p != -1:
                        continue
                    temp_ai.append(item)
                    temp_ai.remove(node)
                    result, _, _ = _mini_max_ab(temp_ai, ara_human, depth - 1, False, alpha, beta)
                    if result > maxEle:
                        maxEle = result
                        best_item = item
                        best_node = node

                    # alpha-beta update and prune
                    alpha = max(alpha, result)
                    if beta <= alpha:
                        break
                if beta <= alpha:
                    break
        # if no moves were found, return very low score (same shape as original)
        if best_item is None:
            return maxEle, best_item, best_node
        return maxEle, best_item, best_node
    else:
        minEle = math.inf
        best_item = None
        best_node = None
        for node in ara_human:
            val = Heuristic_Val(node, neighbour, ara_ai, ara_human)
            if val == 0:
                continue
            else:
                ara = Empty_Neighbour(node, ara_ai, ara_human)
                for item in ara:
                    temp_human = copy.deepcopy(ara_human)
                    x, y = Find_Match(ara_ai, item)
                    p, q = Find_Match(temp_human, item)
                    if x != -1 or p != -1:
                        continue
                    temp_human.append(item)
                    temp_human.remove(node)
                    result, _, _ = _mini_max_ab(ara_ai, temp_human, depth - 1, True, alpha, beta)
                    if result < minEle:
                        minEle = result
                        best_item = item
                        best_node = node

                    # alpha-beta update and prune
                    beta = min(beta, result)
                    if beta <= alpha:
                        break
                if beta <= alpha:
                    break
        if best_item is None:
            return minEle, best_item, best_node
        return minEle, best_item, best_node

def Mini_Max_Move(ara_ai, ara_human, depth, maxPlayer):
    return _mini_max_ab(ara_ai, ara_human, depth, maxPlayer, -math.inf, math.inf)



class GameState:
    def __init__(self):
        self.ai_beads_position = [top, top_l, top_r, top_t, left_l, right_r]
        self.human_beads_position = [bottom, bottom_l, bottom_r, bottom_t, left_r, right_l]
        self.neighbour = Get_First_Hop_Neighbour()


game_state = GameState()

GAME_MODE_SELECTION = 0
AI_TYPE_SELECTION = 1
GAME_PLAYING = 2
GAME_OVER = 3

MINIMAX_AI = 0
ASTAR_FUZZY_AI = 1

AI_VS_HUMAN = 0
AI_VS_AI = 1


def Game_Loop():
    global screen
    running = True
    clock = pygame.time.Clock()
    
    ara = []
    start_time = pygame.time.get_ticks()
    count_human = 0
    human_cor_x = -1
    human_cor_y = -1
    
    human_move = False
    ai_move = True
    winner = False
    
    current_screen = GAME_MODE_SELECTION
    game_mode = None
    ai_type = None
    ai_vs_ai_simulation = False
    simulation_delay = 500  # Increased from 200ms to 800ms for better visibility
    last_ai_move_time = 0
    ai_vs_ai_stuck_counter = 0
    max_stuck_moves = 10
    move_history = []
    
    # Particle system
    particle_system = ParticleSystem()
    floating_texts = FloatingTextSystem()
    ui_ai_score = 0.0
    ui_human_score = 0.0
    diamond_anim = DiamondAnimation(width // 2, 100, 40)
    
    astar_fuzzy_ai = AStarFuzzyAI(game_state, fast_mode=True)
    astar_fuzzy_ai_full = AStarFuzzyAI(game_state, fast_mode=False)
    
    # Load images
    ai_img = pygame.image.load("robot.png").convert_alpha()
    human_img = pygame.image.load("hacker.png").convert_alpha()
    human_v_ai_img = pygame.image.load("human_v_ai.png").convert_alpha()
    ai_v_ai_img = pygame.image.load("ai_v_ai.png").convert_alpha()
    fuzzy_img = pygame.image.load("fuzzy.png").convert_alpha()
    minimax_img = pygame.image.load("minimax.png").convert_alpha()
    
    # Modern buttons
    # Revert to image buttons on home
    ai_vs_human_btn = ImageButton(width // 2 - 220, height // 2 + 60, human_v_ai_img, 0.12, COLOR_PRIMARY,
                                  label="AI vs Human", label_font=button_font)
    ai_vs_ai_btn = ImageButton(width // 2 + 220, height // 2 + 60, ai_v_ai_img, 0.12, COLOR_SECONDARY,
                               label="AI vs AI", label_font=button_font)
    
    # Revert to image buttons on AI type selection
    minimax_btn = ImageButton(width // 2 - 220, height // 2 + 60, minimax_img, 0.12, COLOR_AI,
                              label="Minimax AI", label_font=button_font)
    astar_fuzzy_btn = ImageButton(width // 2 + 220, height // 2 + 60, fuzzy_img, 0.12, COLOR_HUMAN,
                                  label="MCTS AI", label_font=button_font)
    
    btn_text_color = (240, 245, 255)
    menu_btn = ModernButton(width // 2 - 150, height // 2 + 150, 300, 70, "BACK TO MENU", button_font, COLOR_SECONDARY, COLOR_PRIMARY, text_color=btn_text_color)
    back_btn = ModernButton(50, height - 90, 180, 60, "BACK", button_font, COLOR_SECONDARY, COLOR_PRIMARY, text_color=btn_text_color)
    in_game_back_btn = ModernButton(50, height - 90, 180, 60, "BACK", button_font, COLOR_SECONDARY, COLOR_PRIMARY, text_color=btn_text_color)
    restart_btn = ModernButton(width - 240, height - 90, 180, 60, "RESTART", button_font, COLOR_PRIMARY, COLOR_SECONDARY, text_color=btn_text_color)
    
    valid = False
    last_move_effect = None  # {'start':(x,y),'end':(x,y),'start_time':ms,'duration':ms}
    
    last_fs_check = 0
    while running:
        dt = clock.get_time()
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        # Ensure fullscreen truly fills the desktop in case of DPI/monitor changes
        if current_time - last_fs_check > 1000:
            info = pygame.display.Info()
            scr_w, scr_h = screen.get_size()
            if scr_w != info.current_w or scr_h != info.current_h:
                try:
                    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.SCALED)
                except pygame.error:
                    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            last_fs_check = current_time
        
        # Handle AI moves
        if current_screen == GAME_PLAYING:
            if ai_vs_ai_simulation:
                if current_time - last_ai_move_time > simulation_delay:
                    if ai_vs_ai_stuck_counter >= max_stuck_moves:
                        print("Game stuck - declaring draw")
                        current_screen = GAME_OVER
                        winner = True
                    elif ai_move and not human_move:
                        ara_ai_1 = copy.deepcopy(game_state.ai_beads_position)
                        ara_human_1 = copy.deepcopy(game_state.human_beads_position)
                        result1, i1, n1 = Mini_Max_Move(ara_ai_1, ara_human_1, 2, True)
                        moved = False
                        
                        ai_bead_count = len(game_state.ai_beads_position)
                        human_bead_count = len(game_state.human_beads_position)
                        has_advantage = ai_bead_count > human_bead_count
                        
                        if n1 and i1 and n1 in game_state.ai_beads_position:
                            neighbors = Empty_Neighbour(i1, game_state.ai_beads_position, game_state.human_beads_position)
                            trap_potential = 0
                            for neighbor in neighbors:
                                neighbor_neighbors = Empty_Neighbour(neighbor, game_state.ai_beads_position, game_state.human_beads_position)
                                if len(neighbor_neighbors) <= 1:
                                    trap_potential += 1
                            
                            if trap_potential > 0 or len(neighbors) > 2 or has_advantage:
                                game_state.ai_beads_position.remove(n1)
                                game_state.ai_beads_position.append(i1)
                                particle_system.emit(i1, COLOR_AI, count=15)
                                moved = True
                            else:
                                best_strategic_move = None
                                best_score = -1
                                
                                for bead in game_state.ai_beads_position:
                                    bead_neighbors = Empty_Neighbour(bead, game_state.ai_beads_position, game_state.human_beads_position)
                                    for target in bead_neighbors:
                                        score = 0
                                        target_neighbors = Empty_Neighbour(target, game_state.ai_beads_position, game_state.human_beads_position)
                                        score += len(target_neighbors)
                                        
                                        for tn in target_neighbors:
                                            tn_neighbors = Empty_Neighbour(tn, game_state.ai_beads_position, game_state.human_beads_position)
                                            if len(tn_neighbors) <= 1:
                                                score += 10
                                        
                                        if has_advantage:
                                            score += 20
                                        
                                        if score > best_score:
                                            best_score = score
                                            best_strategic_move = (bead, target)
                                
                                if best_strategic_move:
                                    recent_move = (best_strategic_move[0], best_strategic_move[1])
                                    if recent_move not in move_history[-4:]:
                                        game_state.ai_beads_position.remove(best_strategic_move[0])
                                        game_state.ai_beads_position.append(best_strategic_move[1])
                                        particle_system.emit(best_strategic_move[1], COLOR_AI, count=15)
                                        move_history.append(recent_move)
                                        moved = True
                        
                        if not moved:
                            for bead in game_state.ai_beads_position:
                                neighbors = Empty_Neighbour(bead, game_state.ai_beads_position, game_state.human_beads_position)
                                if neighbors:
                                    game_state.ai_beads_position.remove(bead)
                                    game_state.ai_beads_position.append(neighbors[0])
                                    particle_system.emit(neighbors[0], COLOR_AI, count=15)
                                    move_history.append((bead, neighbors[0]))
                                    moved = True
                                    break
                        
                        if not moved:
                            ai_vs_ai_stuck_counter += 1
                        else:
                            ai_vs_ai_stuck_counter = 0
                        
                        ai_move = False
                        human_move = True
                        last_ai_move_time = current_time
                    elif human_move and not ai_move:
                        astar_fuzzy_ai.update_game_state(game_state.ai_beads_position, game_state.human_beads_position)
                        
                        best_move = astar_fuzzy_ai.get_best_move(game_state.human_beads_position[0] if game_state.human_beads_position else (0, 0))
                        
                        moved = False
                        if best_move and best_move[0] != best_move[1] and best_move[0] in game_state.human_beads_position:
                            recent_move = (best_move[0], best_move[1])
                            if recent_move not in move_history[-4:]:
                                game_state.human_beads_position.remove(best_move[0])
                                game_state.human_beads_position.append(best_move[1])
                                particle_system.emit(best_move[1], COLOR_HUMAN, count=15)
                                move_history.append(recent_move)
                                moved = True
                        
                        if not moved:
                            for bead in game_state.human_beads_position:
                                neighbors = Empty_Neighbour(bead, game_state.ai_beads_position, game_state.human_beads_position)
                                if neighbors:
                                    game_state.human_beads_position.remove(bead)
                                    game_state.human_beads_position.append(neighbors[0])
                                    particle_system.emit(neighbors[0], COLOR_HUMAN, count=15)
                                    move_history.append((bead, neighbors[0]))
                                    moved = True
                                    break
                        
                        if not moved:
                            ai_vs_ai_stuck_counter += 1
                        else:
                            ai_vs_ai_stuck_counter = 0
                        
                        ai_move = True
                        human_move = False
                        last_ai_move_time = current_time
            else:
                if ai_move == False and human_move == True:
                    if ai_type == MINIMAX_AI:
                        ara_ai_1 = copy.deepcopy(game_state.ai_beads_position)
                        ara_human_1 = copy.deepcopy(game_state.human_beads_position)
                        result1, i1, n1 = Mini_Max_Move(ara_ai_1, ara_human_1, 4, True)
                        if n1 and i1:
                            game_state.ai_beads_position.remove(n1)
                            game_state.ai_beads_position.append(i1)
                            particle_system.emit(i1, COLOR_AI, count=20)
                    elif ai_type == ASTAR_FUZZY_AI:
                        astar_fuzzy_ai_full.update_game_state(game_state.ai_beads_position, game_state.human_beads_position)
                        
                        best_move = astar_fuzzy_ai_full.get_best_move(game_state.ai_beads_position[0] if game_state.ai_beads_position else (0, 0))
                        
                        if best_move and best_move[0] != best_move[1] and best_move[0] in game_state.ai_beads_position:
                            game_state.ai_beads_position.remove(best_move[0])
                            game_state.ai_beads_position.append(best_move[1])
                            particle_system.emit(best_move[1], COLOR_AI, count=20)
                            last_move_effect = {'start': best_move[0], 'end': best_move[1], 'start_time': current_time, 'duration': 700}
                        else:
                            for bead in game_state.ai_beads_position:
                                neighbors = Empty_Neighbour(bead, game_state.ai_beads_position, game_state.human_beads_position)
                                if neighbors:
                                    game_state.ai_beads_position.remove(bead)
                                    game_state.ai_beads_position.append(neighbors[0])
                                    particle_system.emit(neighbors[0], COLOR_AI, count=20)
                                    last_move_effect = {'start': bead, 'end': neighbors[0], 'start_time': current_time, 'duration': 700}
                                    break
                    
                    ai_move = True
                    human_move = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_screen == GAME_PLAYING:
                        current_screen = GAME_MODE_SELECTION
                        game_state.ai_beads_position = [top, top_l, top_r, top_t, left_l, right_r]
                        game_state.human_beads_position = [bottom, bottom_l, bottom_r, bottom_t, left_r, right_l]
                        ai_move = True
                        human_move = False
                        winner = False
                        ai_vs_ai_simulation = False
                        particle_system.emit((width // 2, height // 2), COLOR_PRIMARY, count=50, velocity_range=8)
                    else:
                        running = False
                elif event.key == pygame.K_F11:
                    # Force fullscreen to desktop size
                    info = pygame.display.Info()
                    try:
                        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.SCALED)
                    except pygame.error:
                        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if current_screen == GAME_MODE_SELECTION:
                        if ai_vs_human_btn.update(mouse_pos, True):
                            game_mode = AI_VS_HUMAN
                            current_screen = AI_TYPE_SELECTION
                            particle_system.emit(mouse_pos, COLOR_PRIMARY, count=30)
                        elif ai_vs_ai_btn.update(mouse_pos, True):
                            game_mode = AI_VS_AI
                            ai_vs_ai_simulation = True
                            current_screen = GAME_PLAYING
                            ai_move = True
                            human_move = False
                            last_ai_move_time = pygame.time.get_ticks()
                            ai_vs_ai_stuck_counter = 0
                            astar_fuzzy_ai.update_game_state(game_state.ai_beads_position, game_state.human_beads_position)
                            particle_system.emit(mouse_pos, COLOR_SECONDARY, count=30)
                    
                    elif current_screen == AI_TYPE_SELECTION:
                        if minimax_btn.update(mouse_pos, True):
                            ai_type = MINIMAX_AI
                            current_screen = GAME_PLAYING
                            particle_system.emit(mouse_pos, COLOR_AI, count=30)
                        elif astar_fuzzy_btn.update(mouse_pos, True):
                            ai_type = ASTAR_FUZZY_AI
                            current_screen = GAME_PLAYING
                            astar_fuzzy_ai_full.update_game_state(game_state.ai_beads_position, game_state.human_beads_position)
                            particle_system.emit(mouse_pos, COLOR_HUMAN, count=30)
                        elif back_btn.update(mouse_pos, True):
                            current_screen = GAME_MODE_SELECTION
                            particle_system.emit(mouse_pos, COLOR_SECONDARY, count=20)
                    
                    elif current_screen == GAME_PLAYING and not ai_vs_ai_simulation:
                        # In-game back button click
                        if in_game_back_btn.update(mouse_pos, True):
                            # Return to previous page depending on mode
                            if game_mode == AI_VS_HUMAN:
                                current_screen = AI_TYPE_SELECTION
                            else:
                                current_screen = GAME_MODE_SELECTION
                            # Reset core game state for a fresh selection
                            game_state.ai_beads_position = [top, top_l, top_r, top_t, left_l, right_r]
                            game_state.human_beads_position = [bottom, bottom_l, bottom_r, bottom_t, left_r, right_l]
                            ai_move = True
                            human_move = False
                            winner = False
                            ai_vs_ai_simulation = False
                            particle_system.emit(mouse_pos, COLOR_SECONDARY, count=30)
                            continue
                        if count_human == 1 and ai_move == True and human_move == False:
                            node = (human_cor_x, human_cor_y)
                            ara = Empty_Neighbour(node, game_state.ai_beads_position, game_state.human_beads_position)
                            
                            x, y = Find_Match(game_state.ai_beads_position, mouse_pos)
                            if x != -1:
                                count_human = 0
                                human_cor_x = -1
                                human_cor_y = -1
                                continue
                            x, y = Find_Match(game_state.human_beads_position, mouse_pos)
                            if x != -1:
                                count_human = 0
                                human_cor_x = -1
                                human_cor_y = -1
                                continue
                            valid = False
                            valid_path = neighbour[(human_cor_x, human_cor_y)]
                            x, y = Find_Match(valid_path, mouse_pos)
                            
                            if x != -1:
                                game_state.human_beads_position.remove((human_cor_x, human_cor_y))
                                game_state.human_beads_position.append((x, y))
                                particle_system.emit((x, y), COLOR_HUMAN, count=25)
                                human_move = True
                                ai_move = False
                            count_human = 0
                            human_cor_x = -1
                            human_cor_y = -1
                            continue
                        if count_human == 0 and ai_move == True and human_move == False:
                            x, y = Find_Match(game_state.human_beads_position, mouse_pos)
                            if x != -1:
                                count_human += 1
                                human_cor_x = x
                                human_cor_y = y
                                valid = True
                                ara = Empty_Neighbour((human_cor_x, human_cor_y), game_state.ai_beads_position, game_state.human_beads_position)
                                particle_system.emit((x, y), COLOR_HUMAN, count=10)
                        # Restart button click during gameplay
                        if restart_btn.update(mouse_pos, True):
                            game_state.ai_beads_position = [top, top_l, top_r, top_t, left_l, right_r]
                            game_state.human_beads_position = [bottom, bottom_l, bottom_r, bottom_t, left_r, right_l]
                            ai_move = True
                            human_move = False
                            winner = False
                            ai_vs_ai_simulation = False
                            move_history.clear()
                            ai_vs_ai_stuck_counter = 0
                            particle_system.emit(mouse_pos, COLOR_ACCENT, count=40)
                    
                    elif current_screen == GAME_OVER:
                        if menu_btn.update(mouse_pos, True):
                            current_screen = GAME_MODE_SELECTION
                            game_state.ai_beads_position = [top, top_l, top_r, top_t, left_l, right_r]
                            game_state.human_beads_position = [bottom, bottom_l, bottom_r, bottom_t, left_r, right_l]
                            ai_move = True
                            human_move = False
                            winner = False
                            ai_vs_ai_simulation = False
                            particle_system.emit((width // 2, height // 2), COLOR_ACCENT, count=100, velocity_range=10)
        
        # Update
        particle_system.update()
        floating_texts.update()
        diamond_anim.update()
        
        # Draw
        ModernUI.draw_futuristic_background(screen, current_time)
        # Unified top UI offset (no persistent title bar)
        top_ui_y = 10
        
        if current_screen == GAME_MODE_SELECTION:
            diamond_anim.draw(screen)
            ModernUI.draw_glowing_text(screen, "DIAMOND CHASE", font, COLOR_PRIMARY,
                                      (width // 2, 240), glow_intensity=1)
            
            ai_vs_human_btn.update(mouse_pos, False)
            ai_vs_ai_btn.update(mouse_pos, False)
            ai_vs_human_btn.draw(screen)
            ai_vs_ai_btn.draw(screen)
        
        elif current_screen == AI_TYPE_SELECTION:
            ModernUI.draw_glowing_text(screen, "Select AI Type", font, COLOR_PRIMARY,
                                      (width // 2, 220), glow_intensity=1)
            
            minimax_btn.update(mouse_pos, False)
            astar_fuzzy_btn.update(mouse_pos, False)
            minimax_btn.draw(screen)
            astar_fuzzy_btn.draw(screen)
            
            back_btn.update(mouse_pos, False)
            back_btn.draw(screen)
        
        elif current_screen == GAME_PLAYING:
            # Trap beads
            for item in game_state.ai_beads_position[:]:
                x, y = Trap_Beads(item[0], item[1], neighbour, RED, game_state.ai_beads_position, game_state.human_beads_position)
                if x == 0 and y != 0:
                    game_state.ai_beads_position.remove(item)
                    particle_system.emit(item, COLOR_AI, count=30, velocity_range=6)
                    particle_system.emit_confetti(item, COLOR_AI, count=28)
                    # Opposite color for +1 to stand out (player gains when AI loses)
                    floating_texts.spawn("+1", item, COLOR_HUMAN)
            
            for item in game_state.human_beads_position[:]:
                x, y = Trap_Beads(item[0], item[1], neighbour, GREEN, game_state.ai_beads_position, game_state.human_beads_position)
                if x == 0 and y > 0:
                    game_state.human_beads_position.remove(item)
                    particle_system.emit(item, COLOR_HUMAN, count=30, velocity_range=6)
                    particle_system.emit_confetti(item, COLOR_HUMAN, count=28)
                    # Opposite color for +1 (AI gains when player loses)
                    floating_texts.spawn("+1", item, COLOR_AI)
            
            len_ai = len(game_state.ai_beads_position)
            len_human = len(game_state.human_beads_position)
            
            # Count-up animation and draw score panels
            target_ai = 6 - len_human
            target_player = 6 - len_ai
            ui_ai_score += (target_ai - ui_ai_score) * 0.25
            ui_human_score += (target_player - ui_human_score) * 0.25
            disp_ai = int(round(ui_ai_score))
            disp_player = int(round(ui_human_score))
            if ai_vs_ai_simulation:
                # AI 1 (Minimax) controls AI beads, so its score is based on human pieces lost
                draw_score_panel(screen, "AI 1 (Minimax)", disp_ai, (50, 50), COLOR_AI, current_time)
                # AI 2 (MCTS) controls human beads, so its score is based on AI pieces lost
                draw_score_panel(screen, "AI 2 (MCTS)", disp_player, (width - 330, 50), COLOR_HUMAN, current_time)
            else:
                # AI Score shows human pieces captured by AI
                draw_score_panel(screen, "AI Score", disp_ai, (50, 50), COLOR_AI, current_time)
                # Player Score shows AI pieces captured by player
                draw_score_panel(screen, "Player Score", disp_player, (width - 330, 50), COLOR_HUMAN, current_time)

            # In-game Back and Restart buttons only for human play (hide in AI vs AI)
            if not ai_vs_ai_simulation:
                in_game_back_btn.update(mouse_pos, False)
                in_game_back_btn.draw(screen)
                restart_btn.update(mouse_pos, False)
                restart_btn.draw(screen)
            
            if valid == True:
                for item in ara:
                    ModernUI.draw_glowing_circle(screen, COLOR_OPTION, item, 10, glow_layers=4)
            
            ModernUI.draw_glowing_line(screen, COLOR_PRIMARY, top, bottom, width=2)
            ModernUI.draw_glowing_line(screen, COLOR_PRIMARY, right, left, width=2)
            
            Draw_Polygon()
            Draw_Circle(game_state.human_beads_position, GREEN)
            Draw_Circle(game_state.ai_beads_position, RED)
            # (line glow effect removed per request)
            
            ModernUI.draw_glowing_text(screen, "Click a piece, then a highlighted node", text_font, WHITE,
                                      (width // 2, 120), glow_intensity=1)
            
            val = Check_Winner(game_state.ai_beads_position, game_state.human_beads_position)
            if val != -1:
                winner = True
                current_screen = GAME_OVER
                particle_system.emit((width // 2, height // 2), 
                                   COLOR_HUMAN if val == 0 else COLOR_AI, count=100, velocity_range=10)
        
        elif current_screen == GAME_OVER:
            val = Check_Winner(game_state.ai_beads_position, game_state.human_beads_position)
            if val == 1:
                if ai_vs_ai_simulation:
                    ModernUI.draw_glowing_text(screen, "AI 1 (Minimax) WINS!", text_font_won, COLOR_AI,
                                              (width // 2, height // 2 - 100), glow_intensity=5)
                else:
                    ModernUI.draw_glowing_text(screen, "AI WINS!", text_font_won, COLOR_AI,
                                              (width // 2, height // 2 - 100), glow_intensity=5)
            elif val == 0:
                if ai_vs_ai_simulation:
                    ModernUI.draw_glowing_text(screen, "AI 2 (MCTS) WINS!", text_font_won, COLOR_HUMAN,
                                              (width // 2, height // 2 - 100), glow_intensity=5)
                else:
                    ModernUI.draw_glowing_text(screen, "YOU WIN!", text_font_won, COLOR_HUMAN,
                                              (width // 2, height // 2 - 100), glow_intensity=5)
            
            menu_btn.update(mouse_pos, False)
            menu_btn.draw(screen)
        
        particle_system.draw(screen)
        floating_texts.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


Game_Loop()