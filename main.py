from reader import read_election_data
from classes import Election

import pygame
import time
import json
import numpy as np

fake_test = False

FAKE_FILE = "Fake Data/test_fake_data.csv"
REAL_FILE = "Data/test_real_data.csv"
NU_PURPLE = (78, 42, 132)
with open("Data/colors.json", "r") as f:
    CAMPAIGN_COLORS = json.load(f)

# Parameters
WELCOME_SCREEN_TIME = 8
OBS_START_DELAY = 3
BATCH_WAIT_MIN = 4
BATCH_WAIT_VAR = 2
ROUND_DISPLAY_TIME = 15
N_SPLITS = 7
VAR_SPLITS = 0.2
WIDTH, HEIGHT = 1250, 850

if __name__ == "__main__":
    # --- Pygame UI setup ---
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    # OBS Start delay
    screen.fill((0, 0, 0))
    pygame.display.flip()
    time.sleep(OBS_START_DELAY)
    pygame.display.set_caption("ASG Election Night")
    # Use a modern sans-serif font similar to Anto (Segoe UI is widely available)
    FONT_FAMILY = 'Segoe UI'
    font_header = pygame.font.SysFont(FONT_FAMILY, 48, bold=True)
    font_round = pygame.font.SysFont(FONT_FAMILY, 36, bold=True)
    font_name = pygame.font.SysFont(FONT_FAMILY, 32)
    font_count = pygame.font.SysFont(FONT_FAMILY, 32)
    font_percent = pygame.font.SysFont(FONT_FAMILY, 32, bold=True)
    BG_COLOR = (245, 245, 245)  # Light background
    TEXT_COLOR = (20, 20, 20)   # Dark text
    BAR_BG = (220, 220, 220)    # Light bar background
    # Assign campaign colors (simple hash for demo)
    def get_color(name):
        if name in CAMPAIGN_COLORS:
            return tuple(CAMPAIGN_COLORS[name])
        colors = [
            (220, 38, 38), (37, 99, 235), (16, 185, 129), (234, 179, 8), (168, 85, 247),
            (251, 191, 36), (59, 130, 246), (239, 68, 68), (34, 197, 94), (250, 204, 21)
        ]
        return colors[hash(name) % len(colors)]

    # Parameters for election night simulation
    n_splits = N_SPLITS
    var_splits = VAR_SPLITS
    pygame.mixer.init()
    pygame.mixer.music.load("Assets/Music/cnn.mp3")
    pygame.mixer.music.play(-1)

    BALLOTS_FILE = FAKE_FILE if fake_test else REAL_FILE
    voters, candidates = read_election_data(BALLOTS_FILE)
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

    # Welcome screen
    screen.fill(BG_COLOR)
    header = font_header.render("Welcome to ASG Election Night!", True, TEXT_COLOR)
    screen.blit(header, (40, 60))
    pygame.display.flip()
    welcome_start = time.time()
    while time.time() - welcome_start < WELCOME_SCREEN_TIME:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        pygame.time.wait(50)

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
    time.sleep(1.5)
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


    # --- Responsive round-by-round display ---
    round_num = 1
    round_display_time = ROUND_DISPLAY_TIME
    clock = pygame.time.Clock()
    next_round_time = time.time() + round_display_time
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if round_num > election.last_round:
            break

        # Draw round results
        screen.fill(BG_COLOR)
        office_title = "ASG President"
        # Draw the title in Northwestern purple, centered
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
        # Layout constants for full window width
        color_box_x = 40
        color_box_w = 60
        name_x = color_box_x + color_box_w + 20
        percent_box_w = 100
        percent_box_x = WIDTH - percent_box_w - 40
        # Right-align count to the left edge of the percent box, with a small gap
        count_gap = 20
        count_x = percent_box_x - count_gap
        bar_x = name_x
        bar_w = percent_box_x - bar_x - 30

        for i, candidate in enumerate(sorted_candidates):
            y = start_y + i * row_height
            color = get_color(candidate)
            # Campaign color box
            pygame.draw.rect(screen, color, (color_box_x, y, color_box_w, 60))
            # Name
            name_surf = font_name.render(candidate, True, TEXT_COLOR)
            screen.blit(name_surf, (name_x, y + 10))
            # Raw vote count (right-aligned to percent box)
            count_surf = font_count.render(str(vote_counts[i]), True, TEXT_COLOR)
            count_rect = count_surf.get_rect()
            count_rect.top = y + 10
            count_rect.right = percent_box_x - 10  # 10px gap from percent box
            screen.blit(count_surf, count_rect)
            # Percent box (right-aligned)
            percent_text = f"{percentages[i]:.1f}%"
            pygame.draw.rect(screen, color, (percent_box_x, y, percent_box_w, 60))
            percent_surf = font_percent.render(percent_text, True, (255, 255, 255))
            screen.blit(percent_surf, (percent_box_x + 10, y + 10))
            # Bar at bottom (full width between name and percent)
            bar_width = int(bar_w * (percentages[i] / 100))
            pygame.draw.rect(screen, BAR_BG, (bar_x, y + 50, bar_w, 15))
            pygame.draw.rect(screen, color, (bar_x, y + 50, bar_width, 15))

        pygame.display.flip()
        clock.tick(30)

        if time.time() >= next_round_time:
            round_num += 1
            next_round_time = time.time() + round_display_time

    # Final winner screen
    screen.fill(BG_COLOR)
    winner_text = f"ASG Projects {election.winner} have been elected ASG President!"
    winner_surf = font_header.render(winner_text, True, TEXT_COLOR)
    winner_rect = winner_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(winner_surf, winner_rect)
    pygame.display.flip()
    time.sleep(30)
    pygame.quit()