with open('Statistic on best rugby players 2023-2024.csv', 'r', encoding='ISO-8859-1') as f:
    lines = f.readlines()
for i in range(95, 115):
    print(i+1, repr(lines[i]))
