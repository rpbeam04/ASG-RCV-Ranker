from reader import read_election_data
from classes import Election

import pygame
import time
import json
import numpy as np

fake_test = False

FAKE_FILE = "Fake Data/test_fake_data.csv"
REAL_FILE = "Data/results.csv"
NU_PURPLE = (78, 42, 132)
with open("Data/colors.json", "r") as f:
    CAMPAIGN_COLORS = json.load(f)

# Parameters
WELCOME_SCREEN_TIME = 8
OBS_START_DELAY = 1
INITIAL_ZERO_SCREEN_TIME = 4
BATCH_WAIT_MIN = 3.5
BATCH_WAIT_VAR = 1
ROUND_DISPLAY_TIME = 10
ELIMINATION_SCREEN_TIME = 4
N_SPLITS = 20
VAR_SPLITS = 0.2
WIDTH, HEIGHT = 1250, 850
# Final projection screen duration after the election ends
FINAL_PROJECTION_TIME = 30

# Functions

# --- Projection screen and checkmark functions (must be defined before main block) ---
def show_projection_screen(screen, font_header, font_round, font_name, BG_COLOR, NU_PURPLE, TEXT_COLOR, get_color, WIDTH, HEIGHT,
                           campaign, title, subtitle, checkmark, duration):
    # Layout constants
    box_w = 320
    box_h = 225
    box_x = 80
    box_y = HEIGHT // 2 - box_h // 2
    color = get_color(campaign)
    # Draw background
    screen.fill(BG_COLOR)
    # Draw campaign color box
    pygame.draw.rect(screen, color, (box_x, box_y, box_w, box_h), border_radius=24)
    # Draw checkmark if needed
    if checkmark:
        # Draw a white checkmark at bottom right of box
        check_w, check_h = 48, 48
        check_x = box_x + box_w - check_w - 18
        check_y = box_y + box_h - check_h - 18
        draw_checkmark(screen, check_x, check_y, check_w, check_h)
    # Text to right of box
    text_x = box_x + box_w + 40
    center_y = HEIGHT // 2
    # Subtitle (ASG Projects:)
    subtitle_surf = font_round.render(subtitle, True, TEXT_COLOR)
    subtitle_rect = subtitle_surf.get_rect()
    subtitle_rect.topleft = (text_x, center_y - 48)
    # Campaign name (large)
    campaign_surf = font_header.render(str(campaign), True, color)
    campaign_rect = campaign_surf.get_rect()
    campaign_rect.topleft = (text_x, center_y)
    # Title (smaller, below, black, moved up)
    title_surf = font_name.render(title, True, (0, 0, 0))
    title_rect = title_surf.get_rect()
    # Move up to align with box (was center_y + 64)
    title_rect.topleft = (text_x, center_y + box_h // 2 - 24)
    # Draw all text
    screen.blit(subtitle_surf, subtitle_rect)
    screen.blit(campaign_surf, campaign_rect)
    screen.blit(title_surf, title_rect)
    pygame.display.flip()
    # Wait for duration, process events
    clock = pygame.time.Clock()
    start = time.time()
    while time.time() - start < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        clock.tick(30)

def draw_checkmark(screen, x, y, w, h):
    # Draw a white checkmark in the given box
    # Coordinates are relative to (x, y), size (w, h)
    # Simple checkmark: two lines
    thickness = max(3, w // 12)
    start1 = (x + w * 0.15, y + h * 0.55)
    end1 = (x + w * 0.4, y + h * 0.8)
    start2 = end1
    end2 = (x + w * 0.85, y + h * 0.2)
    pygame.draw.line(screen, (255, 255, 255), start1, end1, thickness)
    pygame.draw.line(screen, (255, 255, 255), start2, end2, thickness)

def draw_projection(screen, font_header, font_round, font_name, BG_COLOR, NU_PURPLE, TEXT_COLOR, get_color, WIDTH, HEIGHT,
                    campaign, title, subtitle, checkmark):
    # Non-blocking draw of a projection overlay (no flips or waits)
    box_w = 320
    box_h = 225
    box_x = 80
    box_y = HEIGHT // 2 - box_h // 2
    color = get_color(campaign)
    # Draw background fill for overlay
    screen.fill(BG_COLOR)
    # Draw campaign color box
    pygame.draw.rect(screen, color, (box_x, box_y, box_w, box_h), border_radius=24)
    # Checkmark
    if checkmark:
        check_w, check_h = 48, 48
        check_x = box_x + box_w - check_w - 18
        check_y = box_y + box_h - check_h - 18
        draw_checkmark(screen, check_x, check_y, check_w, check_h)
    # Text
    text_x = box_x + box_w + 40
    center_y = HEIGHT // 2
    subtitle_surf = font_round.render(subtitle, True, TEXT_COLOR)
    subtitle_rect = subtitle_surf.get_rect()
    subtitle_rect.topleft = (text_x, center_y - 48)
    campaign_surf = font_header.render(str(campaign), True, color)
    campaign_rect = campaign_surf.get_rect()
    campaign_rect.topleft = (text_x, center_y)
    title_surf = font_name.render(title, True, (0, 0, 0))
    title_rect = title_surf.get_rect()
    title_rect.topleft = (text_x, center_y + box_h // 2 - 24)
    screen.blit(subtitle_surf, subtitle_rect)
    screen.blit(campaign_surf, campaign_rect)
    screen.blit(title_surf, title_rect)

if __name__ == "__main__":
    # --- Pygame UI setup ---
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ASG Election Night")
    FONT_FAMILY = 'Segoe UI'
    font_header = pygame.font.SysFont(FONT_FAMILY, 48, bold=True)
    font_round = pygame.font.SysFont(FONT_FAMILY, 36, bold=True)
    font_name = pygame.font.SysFont(FONT_FAMILY, 32)
    font_count = pygame.font.SysFont(FONT_FAMILY, 32)
    font_percent = pygame.font.SysFont(FONT_FAMILY, 32, bold=True)
    BG_COLOR = (245, 245, 245)
    TEXT_COLOR = (20, 20, 20)
    BAR_BG = (220, 220, 220)
    def get_color(name):
        if name in CAMPAIGN_COLORS:
            return tuple(CAMPAIGN_COLORS[name])
        colors = [
            (220, 38, 38), (37, 99, 235), (16, 185, 129), (234, 179, 8), (168, 85, 247),
            (251, 191, 36), (59, 130, 246), (239, 68, 68), (34, 197, 94), (250, 204, 21)
        ]
        return colors[hash(name) % len(colors)]

    n_splits = N_SPLITS
    var_splits = VAR_SPLITS

    BALLOTS_FILE = FAKE_FILE if fake_test else REAL_FILE
    voters, candidates = read_election_data(BALLOTS_FILE)

    # OBS Start delay (unchanged)
    obs_delay_start = time.time()
    clock = pygame.time.Clock()
    while time.time() - obs_delay_start < OBS_START_DELAY:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        clock.tick(30)

    # Start music after OBS
    pygame.mixer.init()
    pygame.mixer.music.load("Assets/Music/cnn.mp3")
    pygame.mixer.music.play(-1)

    # --- Real Intro Animation ---
    import os
    logo_path = os.path.join("Assets", "Images", "logo.png")
    logo_img = pygame.image.load(logo_path).convert_alpha()
    logo_w, logo_h = logo_img.get_size()
    logo_scale = 0.16
    logo_small = pygame.transform.smoothscale(logo_img, (int(logo_w * logo_scale), int(logo_h * logo_scale)))
    logo_w_small, logo_h_small = logo_small.get_size()
    intro_duration = 8.0
    intro_anim_time = 3.0
    intro_start = time.time()
    text_surf = font_header.render("Election Night", True, NU_PURPLE)
    text_rect = text_surf.get_rect()
    # Center logo and text vertically and horizontally
    logo_final_y = HEIGHT // 2 - (logo_h_small + text_rect.height + 30) // 2
    logo_final_x = WIDTH // 2 - logo_w_small // 2
    text_rect.centerx = WIDTH // 2
    text_rect.top = logo_final_y + logo_h_small + 30

    # Animate logo slide/fade in over 3 seconds
    while True:
        elapsed = time.time() - intro_start
        progress = min(elapsed / intro_anim_time, 1.0)
        logo_y = int(-logo_h_small + progress * (logo_final_y + logo_h_small))
        alpha = int(progress * 255)
        logo_img_fade = logo_small.copy()
        logo_img_fade.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        screen.fill(BG_COLOR)
        logo_rect = logo_img_fade.get_rect()
        logo_rect.left = logo_final_x
        logo_rect.top = logo_y
        screen.blit(logo_img_fade, logo_rect)
        if progress == 1.0:
            screen.blit(text_surf, text_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        clock.tick(60)
        if progress == 1.0:
            break

    # Hold logo and text for remaining intro time
    hold_start = time.time()
    while time.time() - hold_start < (intro_duration - intro_anim_time):
        screen.fill(BG_COLOR)
        logo_rect = logo_small.get_rect()
        logo_rect.left = logo_final_x
        logo_rect.top = logo_final_y
        screen.blit(logo_small, logo_rect)
        screen.blit(text_surf, text_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        clock.tick(60)

    # --- Simulate round 1 results coming in batches ---
    total_voters = len(voters)
    avg_split = total_voters // n_splits
    split_sizes = []
    remaining = total_voters
    for i in range(n_splits):
        if i == n_splits - 1:
            split_sizes.append(remaining)
        else:
            # Add random variation
            var = int(avg_split * var_splits)
            size = avg_split + np.random.randint(-var, var + 1)
            size = max(1, min(size, remaining - (n_splits - i - 1)))
            split_sizes.append(size)
            remaining -= size
    split_indexes = [sum(split_sizes[:i+1]) for i in range(n_splits)]

    # ...existing code...

    # Initial screen: 0% of vote in
    screen.fill(BG_COLOR)
    office_title = "ASG President"
    header = font_header.render(office_title, True, NU_PURPLE)
    header_rect = header.get_rect()
    header_rect.topleft = (40, 20)
    screen.blit(header, header_rect)
    round_label = font_round.render("Round 1 Results", True, TEXT_COLOR)
    screen.blit(round_label, (40, 90))

    # Draw candidate rows manually
    row_height = 80
    start_y = 160
    color_box_x = 40
    color_box_w = 60
    name_x = color_box_x + color_box_w + 20
    percent_box_w = 100
    percent_box_x = WIDTH - percent_box_w - 40
    count_gap = 20
    count_x = percent_box_x - count_gap
    bar_x = name_x
    bar_w = percent_box_x - bar_x - 30

    for i, candidate in enumerate(candidates):
        y = start_y + i * row_height
        color = get_color(candidate)
        pygame.draw.rect(screen, color, (color_box_x, y, color_box_w, 60))
        name_surf = font_name.render(candidate, True, TEXT_COLOR)
        screen.blit(name_surf, (name_x, y + 10))
        # Raw vote count (right-aligned to percent box)
        count_surf = font_count.render("0", True, TEXT_COLOR)
        count_rect = count_surf.get_rect()
        count_rect.top = y + 10
        count_rect.right = percent_box_x - 10
        screen.blit(count_surf, count_rect)
        # Percent box (right-aligned)
        percent_text = "0.0%"
        pygame.draw.rect(screen, color, (percent_box_x, y, percent_box_w, 60))
        percent_surf = font_percent.render(percent_text, True, (255, 255, 255))
        screen.blit(percent_surf, (percent_box_x + 10, y + 10))
        # Bar at bottom (full width between name and percent)
        pygame.draw.rect(screen, BAR_BG, (bar_x, y + 50, bar_w, 15))
        # No fill for 0%

    # Draw 0% bar
    bar_in_w = 120
    bar_in_h = 10
    bar_in_x = WIDTH - bar_in_w - 40
    bar_in_y = start_y + len(candidates) * row_height + 20
    pygame.draw.rect(screen, BAR_BG, (bar_in_x, bar_in_y, bar_in_w, bar_in_h))
    percent_in_text = "0% of vote in"
    percent_in_surf = font_round.render(percent_in_text, True, NU_PURPLE)
    percent_in_rect = percent_in_surf.get_rect()
    percent_in_rect.right = bar_in_x + bar_in_w
    percent_in_rect.top = bar_in_y + bar_in_h + 2
    screen.blit(percent_in_surf, percent_in_rect)
    pygame.display.flip()
    zero_screen_start = time.time()
    clock = pygame.time.Clock()
    while time.time() - zero_screen_start < INITIAL_ZERO_SCREEN_TIME:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        clock.tick(30)
    # No extra clear or frame wait; transition directly to first batch

    # Simulate partial results for round 1
    partial_voters = []
    clock = pygame.time.Clock()
    for batch_num, split_idx in enumerate(split_indexes):
        partial_voters = voters[:split_idx]
        partial_election = Election(partial_voters, candidates)
        partial_election.run_election()
        df = partial_election.get_round_vote_counts(1)
        sorted_candidates = list(df.index)
        vote_counts = [df.iloc[i, 0] if not isinstance(df.iloc[i, 0], str) else 0 for i in range(len(df))]
        total_votes = sum(vote_counts)
        percentages = [(v / total_votes * 100) if total_votes > 0 else 0 for v in vote_counts]

        # Draw partial results
        screen.fill(BG_COLOR)
        office_title = "ASG President"
        header = font_header.render(office_title, True, NU_PURPLE)
        header_rect = header.get_rect()
        header_rect.topleft = (40, 20)
        screen.blit(header, header_rect)
        round_label = font_round.render("Round 1 Results", True, TEXT_COLOR)
        screen.blit(round_label, (40, 90))

        row_height = 80
        start_y = 160
        color_box_x = 40
        color_box_w = 60
        name_x = color_box_x + color_box_w + 20
        percent_box_w = 100
        percent_box_x = WIDTH - percent_box_w - 40
        count_gap = 20
        count_x = percent_box_x - count_gap
        bar_x = name_x
        bar_w = percent_box_x - bar_x - 30

        for i, candidate in enumerate(sorted_candidates):
            y = start_y + i * row_height
            color = get_color(candidate)
            pygame.draw.rect(screen, color, (color_box_x, y, color_box_w, 60))
            name_surf = font_name.render(candidate, True, TEXT_COLOR)
            screen.blit(name_surf, (name_x, y + 10))
            count_surf = font_count.render(str(vote_counts[i]), True, TEXT_COLOR)
            count_rect = count_surf.get_rect()
            count_rect.top = y + 10
            count_rect.right = percent_box_x - 10
            screen.blit(count_surf, count_rect)
            percent_text = f"{percentages[i]:.1f}%"
            pygame.draw.rect(screen, color, (percent_box_x, y, percent_box_w, 60))
            percent_surf = font_percent.render(percent_text, True, (255, 255, 255))
            screen.blit(percent_surf, (percent_box_x + 10, y + 10))
            bar_width = int(bar_w * (percentages[i] / 100))
            pygame.draw.rect(screen, BAR_BG, (bar_x, y + 50, bar_w, 15))
            pygame.draw.rect(screen, color, (bar_x, y + 50, bar_width, 15))

        # Add a small right-aligned bar below the last candidate showing % of vote in, only if not full vote
        percent_in = split_idx / total_voters if total_voters > 0 else 0
        if percent_in < 1.0:
            bar_in_w = 120
            bar_in_h = 10
            bar_in_x = WIDTH - bar_in_w - 40
            bar_in_y = start_y + len(sorted_candidates) * row_height + 20
            pygame.draw.rect(screen, BAR_BG, (bar_in_x, bar_in_y, bar_in_w, bar_in_h))
            pygame.draw.rect(screen, NU_PURPLE, (bar_in_x, bar_in_y, int(bar_in_w * percent_in), bar_in_h))
            percent_in_text = f"{int(percent_in * 100)}% of vote in"
            percent_in_surf = font_round.render(percent_in_text, True, NU_PURPLE)
            percent_in_rect = percent_in_surf.get_rect()
            percent_in_rect.right = bar_in_x + bar_in_w
            percent_in_rect.top = bar_in_y + bar_in_h + 2
            screen.blit(percent_in_surf, percent_in_rect)

        pygame.display.flip()
        # Wait for a short time for each batch
        batch_wait = BATCH_WAIT_MIN + np.random.uniform(0, BATCH_WAIT_VAR)
        start_time = time.time()
        # Show first batch immediately after title screen
        if batch_num == 0:
            pass
        while time.time() - start_time < batch_wait:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            clock.tick(30)

    # After all partial batches, run full election
    election = Election(voters, candidates)
    election.run_election()


    # --- Responsive round-by-round display with projection screens ---
    round_num = 1
    round_display_time = ROUND_DISPLAY_TIME
    clock = pygame.time.Clock()
    next_round_time = time.time() + round_display_time
    running = True
    while running:
        # Draw round results
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if round_num > election.last_round:
            break

        screen.fill(BG_COLOR)
        office_title = "ASG President"
        header = font_header.render(office_title, True, NU_PURPLE)
        header_rect = header.get_rect()
        header_rect.topleft = (40, 20)
        screen.blit(header, header_rect)
        round_label = font_round.render(f"Round {round_num} Results", True, TEXT_COLOR)
        screen.blit(round_label, (40, 90))

        df = election.get_round_vote_counts(round_num)
        sorted_candidates = list(df.index)
        vote_counts = [df.iloc[i, 0] if not isinstance(df.iloc[i, 0], str) else 0 for i in range(len(df))]
        total_votes = sum(vote_counts)
        percentages = [(v / total_votes * 100) if total_votes > 0 else 0 for v in vote_counts]

        row_height = 80
        start_y = 160
        color_box_x = 40
        color_box_w = 60
        name_x = color_box_x + color_box_w + 20
        percent_box_w = 100
        percent_box_x = WIDTH - percent_box_w - 40
        count_gap = 20
        count_x = percent_box_x - count_gap
        bar_x = name_x
        bar_w = percent_box_x - bar_x - 30

        for i, candidate in enumerate(sorted_candidates):
            y = start_y + i * row_height
            color = get_color(candidate)
            pygame.draw.rect(screen, color, (color_box_x, y, color_box_w, 60))
            name_surf = font_name.render(candidate, True, TEXT_COLOR)
            screen.blit(name_surf, (name_x, y + 10))
            count_surf = font_count.render(str(vote_counts[i]), True, TEXT_COLOR)
            count_rect = count_surf.get_rect()
            count_rect.top = y + 10
            count_rect.right = percent_box_x - 10
            screen.blit(count_surf, count_rect)
            percent_text = f"{percentages[i]:.1f}%"
            pygame.draw.rect(screen, color, (percent_box_x, y, percent_box_w, 60))
            percent_surf = font_percent.render(percent_text, True, (255, 255, 255))
            screen.blit(percent_surf, (percent_box_x + 10, y + 10))
            bar_width = int(bar_w * (percentages[i] / 100))
            pygame.draw.rect(screen, BAR_BG, (bar_x, y + 50, bar_w, 15))
            pygame.draw.rect(screen, color, (bar_x, y + 50, bar_width, 15))

        pygame.display.flip()
        clock.tick(30)

        # --- Manual majority/plurality/elimination check ---
        majority = False
        winner = None
        if total_votes > 0:
            for i, pct in enumerate(percentages):
                if pct > 50.0:
                    majority = True
                    winner = sorted_candidates[i]
                    break
        eliminated = None
        if len(sorted_candidates) > 0:
            eliminated = sorted_candidates[-1]
        plurality = sorted_candidates[0] if sorted_candidates else None

        # Show the results for the configured round display time BEFORE projections
        round_display_start = time.time()
        while time.time() - round_display_start < round_display_time:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            # redraw current round results during countdown so screen isn't static
            screen.fill(BG_COLOR)
            office_title = "ASG President"
            header = font_header.render(office_title, True, NU_PURPLE)
            header_rect = header.get_rect()
            header_rect.topleft = (40, 20)
            screen.blit(header, header_rect)
            round_label = font_round.render(f"Round {round_num} Results", True, TEXT_COLOR)
            screen.blit(round_label, (40, 90))

            # draw the same results again
            for i, candidate in enumerate(sorted_candidates):
                y = start_y + i * row_height
                color = get_color(candidate)
                pygame.draw.rect(screen, color, (color_box_x, y, color_box_w, 60))
                name_surf = font_name.render(candidate, True, TEXT_COLOR)
                screen.blit(name_surf, (name_x, y + 10))
                count_surf = font_count.render(str(vote_counts[i]), True, TEXT_COLOR)
                count_rect = count_surf.get_rect()
                count_rect.top = y + 10
                count_rect.right = percent_box_x - 10
                screen.blit(count_surf, count_rect)
                percent_text = f"{percentages[i]:.1f}%"
                pygame.draw.rect(screen, color, (percent_box_x, y, percent_box_w, 60))
                percent_surf = font_percent.render(percent_text, True, (255, 255, 255))
                screen.blit(percent_surf, (percent_box_x + 10, y + 10))
                bar_width = int(bar_w * (percentages[i] / 100))
                pygame.draw.rect(screen, BAR_BG, (bar_x, y + 50, bar_w, 15))
                pygame.draw.rect(screen, color, (bar_x, y + 50, bar_width, 15))

            pygame.display.flip()
            clock.tick(30)

        # Queue projection screens and render them non-blocking in the main loop
        projection_queue = []
        if majority:
            projection_queue.append({
                'campaign': winner,
                'title': 'Elected ASG Presidents',
                'subtitle': 'ASG Projects:',
                'checkmark': True,
                'duration': ELIMINATION_SCREEN_TIME
            })
        else:
            # plurality then eliminated
            projection_queue.append({
                'campaign': plurality,
                'title': f'Wins Plurality of Round {round_num}',
                'subtitle': 'ASG Projects:',
                'checkmark': True,
                'duration': ELIMINATION_SCREEN_TIME
            })
            projection_queue.append({
                'campaign': eliminated,
                'title': f'Eliminated Round {round_num}',
                'subtitle': 'ASG Projects:',
                'checkmark': False,
                'duration': ELIMINATION_SCREEN_TIME
            })

        # Run the queued projections sequentially without blocking the rest of the app
        while projection_queue:
            proj = projection_queue.pop(0)
            proj_end = time.time() + proj['duration']
            # render loop for this projection
            while time.time() < proj_end:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                draw_projection(screen, font_header, font_round, font_name, BG_COLOR, NU_PURPLE, TEXT_COLOR, get_color, WIDTH, HEIGHT,
                                proj['campaign'], proj['title'], proj['subtitle'], proj['checkmark'])
                pygame.display.flip()
                clock.tick(30)

        # After all projections finished, clear and ensure compositor updates
        screen.fill(BG_COLOR)
        pygame.display.flip()
        pygame.event.pump()
        pygame.time.delay(50)
        pygame.display.flip()

        # advance to next round
        round_num += 1

    # --- Final projection after election ends ---
    # Show final winner/projection for a configurable duration
    try:
        final_df = election.get_round_vote_counts(election.last_round)
        final_sorted = list(final_df.index)
        final_votes = [final_df.iloc[i, 0] if not isinstance(final_df.iloc[i, 0], str) else 0 for i in range(len(final_df))]
        total_votes = sum(final_votes)
        final_winner = final_sorted[0] if (final_sorted and total_votes > 0) else None
    except Exception:
        final_winner = None

    if final_winner:
        final_end = time.time() + FINAL_PROJECTION_TIME
        while time.time() < final_end:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            draw_projection(screen, font_header, font_round, font_name, BG_COLOR, NU_PURPLE, TEXT_COLOR, get_color, WIDTH, HEIGHT,
                            final_winner, 'Elected ASG Presidents', 'ASG Projects:', True)
            pygame.display.flip()
            clock.tick(30)

    pygame.quit()
