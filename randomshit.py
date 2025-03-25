import time, os, random

WIDTH, HEIGHT = 20, 20
board = [[random.randint(0,1) for _ in range(WIDTH)] for _ in range(HEIGHT)]

try:
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        # 🧠 First, update the board just ONCE
        exec(f'{globals().__setitem__("board", [[(lambda c,n: 1 if c and 2<=n<=3 or not c and n==3 else 0)(board[y][x], sum(board[(y+dy)%HEIGHT][(x+dx)%WIDTH] for dx in (-1,0,1) for dy in (-1,0,1) if dx or dy)) for x in range(WIDTH)] for y in range(HEIGHT)])}')

        # 🖼️ Then, render the updated board
        print('\n'.join(
            ''.join('⬜' if cell else '  ' for cell in row)
            for row in board
        ))

        time.sleep(0.3)

except KeyboardInterrupt:
    print("☠️ You survived the Great Flickering.")
