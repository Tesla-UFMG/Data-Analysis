import pandas as pd
import matplotlib.pyplot as plt

SAMPLING_FREQ = 2.048e6
VOLTAGE_THRESHHOLD = 5

# path = "dados_encoder/frente_5ms.xlsx"
path = "dados_encoder/frente_50ms.xlsx"
# path = "dados_encoder/frente_breno.xlsx"
# path = "dados_encoder/tras_5ms.xlsx"

# Read Excel file (requires openpyxl to be installed)
df = pd.read_excel(path, engine='openpyxl')

range_to_plot = range(1, len(df.iloc[:, 0]))
# range_to_plot = range(5000, 6000)

# le os valores todos - serao lidos como string
time = df.iloc[range_to_plot, 0]
ch1 = df.iloc[range_to_plot, 1]
ch2 = df.iloc[range_to_plot, 2]
ch3 = df.iloc[range_to_plot, 3]

# converte as string para float

for i in range_to_plot:
    time[i] = float(time[i]) - min(df.iloc[range_to_plot, 0]) / SAMPLING_FREQ * 1e3
    ch1[i] = float(ch1[i])
    ch2[i] = float(ch2[i])
    ch3[i] = float(ch3[i])

previous_v = 0
previous_egde = time[1]
freq_list = []
first_loop = True
for i in range_to_plot:
    curr_v = ch1[i]
    curr_t = time[i]

    if first_loop:
        previous_v = curr_v
        first_loop = False
        next

    if abs(curr_v - previous_v) >= VOLTAGE_THRESHHOLD:
        # we have an edge
        freq = curr_t - previous_egde
        previous_egde = curr_t
        freq_list.append(freq)

    previous_v = curr_v

# Plot multiple lines
# plt.plot(time, ch1, label='CH 1', color='red', linestyle='-')
# plt.plot(time, ch2, label='CH 2', color='green', linestyle='--')

# Add titles and labels
# plt.xlabel('Tempo (ms)')
# plt.ylabel('CH (V)')

plt.plot(freq_list, label='Frequência', color='red', linestyle='-')
plt.xlabel('Index')
plt.ylabel('Frequência (Hz)')

# Show the plot
plt.show()
