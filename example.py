
min_price_tick = 0.0001
min_price_tick_len = len(str(min_price_tick))
print(min_price_tick_len)
a = 0.1924000002
b = str(a)
print(a)
print(len(b))
print(b[:min_price_tick_len])
print(type(b[:min_price_tick_len]))
c = float(b[:min_price_tick_len])
print(c)
print(type(c))