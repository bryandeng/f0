#!/usr/bin/env python3

import os
import subprocess

# snrs = [20, 15, 10, 5, 0, -5]  # dB
snrs = [20, 15, 10, 5, 0]  # dB

input_basedir = "/home/bdeng/datasets/speechdata_16kHz"
noise_file = "/home/bdeng/datasets/noises_16kHz/concatenated.raw"
output_basedir = ("/home/bdeng/datasets/" +
                  "speechdata_16kHz_with_noise_wrt_snr")
fant_path = "/home/bdeng/Documents/fant/filter_add_noise"

input_raw_basedir = input_basedir + '_raw'
os.makedirs(input_raw_basedir, exist_ok=True)

output_raw_basedir = output_basedir + '_raw'
for snr in snrs:
    os.makedirs(os.path.join(output_basedir, str(snr)), exist_ok=True)
    os.makedirs(os.path.join(output_raw_basedir, str(snr)), exist_ok=True)

wav_filenames = []

for root, dirs, files in os.walk(input_basedir):
    for name in files:
        if name.startswith('mic'):
            wav_filenames.append(name)

raw_filenames = [os.path.splitext(wav_filename)[0] + '.raw'
                 for wav_filename in wav_filenames]

for wav_filename, raw_filename in zip(wav_filenames, raw_filenames):
    subprocess.run(
        ['sox',
         os.path.join(input_basedir, wav_filename),
         os.path.join(input_raw_basedir, raw_filename)]
    )

with open(os.path.join('shelf', 'in.list'), 'w') as in_list:
    in_paths = [os.path.join(input_raw_basedir, raw_filename) + '\n'
                for raw_filename in raw_filenames]
    in_list.writelines(in_paths)

for snr in snrs:
    with open(os.path.join('shelf', 'out_' + str(snr) + 'dB.list'),
              'w') as out_list:
        out_paths = [os.path.join(output_raw_basedir, str(snr),
                                  raw_filename) + '\n'
                     for raw_filename in raw_filenames]
        out_list.writelines(out_paths)

for snr in snrs:
    subprocess.run(
        [fant_path,
         '-i', os.path.join('shelf', 'in.list'),
         '-o', os.path.join('shelf', 'out_' + str(snr) + 'dB.list'),
         '-n', noise_file,
         '-u', '-d',
         '-s', str(snr),
         '-r', '1000']
    )

for snr in snrs:
    for wav_filename, raw_filename in zip(wav_filenames, raw_filenames):
        subprocess.run(
            ['sox', '-r', '16k', '-e', 'signed', '-b', '16', '-c', '1',
             os.path.join(output_raw_basedir, str(snr), raw_filename),
             os.path.join(output_basedir, str(snr), wav_filename)]
        )

print("Done.")
