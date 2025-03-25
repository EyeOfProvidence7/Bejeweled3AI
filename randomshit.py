import os, time, random

print(
    (
        lambda: [
            globals().__setitem__('WIDTH', 20),
            globals().__setitem__('HEIGHT', 20),
            globals().__setitem__('board', [[random.randint(0, 1) for _ in range(20)] for _ in range(20)]),
            globals().__setitem__('depth', 0),
            (lambda: [
                (lambda loop:
                    [  # Real loop, fake recursion aesthetic
                        globals().__setitem__('depth', i + 1),
                        os.system('cls' if os.name == 'nt' else 'clear'),
                        print(f"""FRAME: {globals()['depth']}\n{
                            globals().__setitem__('board',
                                [[(lambda c,n: 1 if c and 2<=n<=3 or not c and n==3 else 0)(
                                    board[y][x],
                                    sum(board[(y+dy)%globals()['HEIGHT']][(x+dx)%globals()['WIDTH']]
                                        for dx in (-1,0,1) for dy in (-1,0,1) if dx or dy)
                                ) for x in range(globals()['WIDTH'])] for y in range(globals()['HEIGHT'])]
                            ) or ''}\n{
                                chr(10).join(
                                    ''.join(f'{"⬜" if board[y][x] else "  "}' for x in range(globals()['WIDTH']))
                                    for y in range(globals()['HEIGHT'])
                                )
                            }"""),
                        time.sleep(0.05)
                    ]
                    for i in iter(int, 1)  # infinite loop: same as while True
                )(None)
            ])
        ]
    )()
)
