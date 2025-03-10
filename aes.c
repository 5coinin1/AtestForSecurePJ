#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define AES_BLOCK_SIZE 16
#define AES_KEY_SIZE 32  // AES-256 sử dụng khóa 32 byte
#define AES_ROUNDS 14    // AES-256 có 14 vòng
#define AES_EXPANDED_KEY_SIZE ((AES_ROUNDS + 1) * AES_BLOCK_SIZE)

// S-Box dùng trong SubBytes
static const uint8_t sbox[256] = {
    // 0     1    2    3    4    5    6    7    8    9    A    B    C    D    E    F
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
};

static const uint8_t rcon[11] = {
    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36
};

void SubBytes(uint8_t state[AES_BLOCK_SIZE]) {
    for (int i = 0; i < AES_BLOCK_SIZE; i++) {
        state[i] = sbox[state[i]];
    }
}

void ShiftRows(uint8_t state[AES_BLOCK_SIZE]) {
    uint8_t temp;
    temp = state[1]; state[1] = state[5]; state[5] = state[9]; state[9] = state[13]; state[13] = temp;
    temp = state[2]; state[2] = state[10]; state[10] = temp;
    temp = state[6]; state[6] = state[14]; state[14] = temp;
    temp = state[3]; state[3] = state[15]; state[15] = state[11]; state[11] = state[7]; state[7] = temp;
}

uint8_t xtime(uint8_t x) {
    return (x << 1) ^ ((x >> 7) * 0x1b);
}

void MixColumns(uint8_t state[AES_BLOCK_SIZE]) {
    for (int i = 0; i < 4; i++) {
        uint8_t *col = &state[i * 4];
        uint8_t t = col[0] ^ col[1] ^ col[2] ^ col[3];

        uint8_t tmp0 = col[0];
        col[0] ^= t ^ xtime(col[0] ^ col[1]);
        col[1] ^= t ^ xtime(col[1] ^ col[2]);
        col[2] ^= t ^ xtime(col[2] ^ col[3]);
        col[3] ^= t ^ xtime(col[3] ^ tmp0);
    }
}


void AddRoundKey(uint8_t state[AES_BLOCK_SIZE], uint8_t roundKey[AES_BLOCK_SIZE]) {
    for (int i = 0; i < AES_BLOCK_SIZE; i++) {
        state[i] ^= roundKey[i];
    }
}

void KeyExpansion(uint8_t key[AES_KEY_SIZE], uint8_t roundKeys[AES_EXPANDED_KEY_SIZE]) {
    memcpy(roundKeys, key, AES_KEY_SIZE);
    uint8_t temp[4];
    int i = AES_KEY_SIZE;
    int rconIndex = 1;
    while (i < AES_EXPANDED_KEY_SIZE) {
        memcpy(temp, &roundKeys[i - 4], 4);
        if (i % AES_KEY_SIZE == 0) {
            uint8_t t = temp[0];
            temp[0] = sbox[temp[1]] ^ rcon[rconIndex++];
            temp[1] = sbox[temp[2]];
            temp[2] = sbox[temp[3]];
            temp[3] = sbox[t];
        } else if (i % AES_KEY_SIZE == 16) {
            temp[0] = sbox[temp[0]];
            temp[1] = sbox[temp[1]];
            temp[2] = sbox[temp[2]];
            temp[3] = sbox[temp[3]];
        }
        for (int j = 0; j < 4; j++) {
            roundKeys[i] = roundKeys[i - AES_KEY_SIZE] ^ temp[j];
            i++;
        }
    }
}

void AES_Encrypt(uint8_t input[AES_BLOCK_SIZE], uint8_t key[AES_KEY_SIZE], uint8_t output[AES_BLOCK_SIZE]) {
    uint8_t state[AES_BLOCK_SIZE];
    uint8_t roundKeys[AES_EXPANDED_KEY_SIZE];
    KeyExpansion(key, roundKeys);
    memcpy(state, input, AES_BLOCK_SIZE);

    // Vòng đầu tiên
    AddRoundKey(state, roundKeys);

    // Vòng lặp chính
    for (int round = 1; round < AES_ROUNDS; round++) {
        SubBytes(state);
        ShiftRows(state);
        MixColumns(state);
        AddRoundKey(state, roundKeys + round * AES_BLOCK_SIZE);
    }

    // Vòng cuối không dùng MixColumns
    SubBytes(state);
    ShiftRows(state);
    AddRoundKey(state, roundKeys + AES_ROUNDS * AES_BLOCK_SIZE);

    memcpy(output, state, AES_BLOCK_SIZE);
}

void AES_Encrypt(uint8_t input[AES_BLOCK_SIZE], uint8_t key[AES_KEY_SIZE], uint8_t output[AES_BLOCK_SIZE]);
void KeyExpansion(uint8_t key[AES_KEY_SIZE], uint8_t roundKeys[AES_EXPANDED_KEY_SIZE]);

void AES_CFB_Encrypt(uint8_t *plaintext, uint8_t *key, uint8_t *iv, uint8_t *ciphertext, int length) {
    uint8_t feedback[AES_BLOCK_SIZE], keystream[AES_BLOCK_SIZE];
    memcpy(feedback, iv, AES_BLOCK_SIZE);

    for (int i = 0; i < length; i += AES_BLOCK_SIZE) {
        AES_Encrypt(feedback, key, keystream);

        for (int j = 0; j < AES_BLOCK_SIZE && i + j < length; j++) {
            ciphertext[i + j] = plaintext[i + j] ^ keystream[j];
            feedback[j] = ciphertext[i + j];
        }
    }
}

void AES_CFB_Decrypt(uint8_t *ciphertext, uint8_t *key, uint8_t *iv, uint8_t *plaintext, int length) {
    uint8_t feedback[AES_BLOCK_SIZE], keystream[AES_BLOCK_SIZE];
    memcpy(feedback, iv, AES_BLOCK_SIZE);

    for (int i = 0; i < length; i += AES_BLOCK_SIZE) {
        AES_Encrypt(feedback, key, keystream);

        for (int j = 0; j < AES_BLOCK_SIZE && i + j < length; j++) {
            plaintext[i + j] = ciphertext[i + j] ^ keystream[j];
            feedback[j] = ciphertext[i + j];  // Cập nhật feedback với ciphertext
        }
    }
}


// Hàm public để gọi từ Python
void decrypt_cfb(uint8_t *ciphertext, uint8_t *key, uint8_t *iv, uint8_t *plaintext, int length) {
    AES_CFB_Decrypt(ciphertext, key, iv, plaintext, length);
}

void encrypt_cfb(uint8_t *plaintext, uint8_t *key, uint8_t *iv, uint8_t *ciphertext, int length) {
    AES_CFB_Encrypt(plaintext, key, iv, ciphertext, length);
}
