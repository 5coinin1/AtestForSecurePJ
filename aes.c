#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define AES_BLOCK_SIZE 16
#define AES_KEY_SIZE 32  // AES-256 sử dụng khóa 32 byte
#define AES_ROUNDS 14    // AES-256 có 14 vòng
#define AES_EXPANDED_KEY_SIZE ((AES_ROUNDS + 1) * AES_BLOCK_SIZE)

// S-Box dùng trong SubBytes
static const uint8_t sbox[256] = {
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
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
    AddRoundKey(state, roundKeys);
    for (int round = 1; round < AES_ROUNDS; round++) {
        SubBytes(state);
        ShiftRows(state);
        AddRoundKey(state, roundKeys + round * AES_BLOCK_SIZE);
    }
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
