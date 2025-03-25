import os, time, random

print(
    (
        lambda: [
            globals().__setitem__('WIDTH', 100),
            globals().__setitem__('HEIGHT', 100),
            globals().__setitem__('board', [[random.randint(0, 1) for _ in range(100)] for _ in range(100)]),
            (lambda loop:
                loop(loop)
            )(lambda self:
                (
                    os.system('cls' if os.name == 'nt' else 'clear'),
                    print(f"""{globals().__setitem__('board',
                        [[(lambda c,n: 1 if c and 2<=n<=3 or not c and n==3 else 0)(
                            board[y][x],
                            sum(board[(y+dy)%HEIGHT][(x+dx)%WIDTH]
                                for dx in (-1,0,1) for dy in (-1,0,1) if dx or dy)
                        ) for x in range(WIDTH)] for y in range(HEIGHT)]
                    ) or ''}\n{
                        chr(10).join(
                            ''.join(f'{"⬜" if board[y][x] else "  "}' for x in range(WIDTH))
                            for y in range(HEIGHT)
                        )
                    }"""),
                    time.sleep(0.1),
                    self(self)  # Recursive lambda = loop
                )
            )
        ]
    )()
)


