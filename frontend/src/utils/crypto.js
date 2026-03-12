/**
 * Web Crypto API 封装 (PBKDF2 + AES-GCM)
 * 用于前端凭证的加密与解密
 */

const ITERATIONS = 100000;
const KEY_LENGTH = 256;
const DIGEST = "SHA-256";

/**
 * 将十六进制字符串转换为 Uint8Array
 */
function hexToBytes(hex) {
    const bytes = new Uint8Array(hex.length / 2);
    for (let i = 0; i < hex.length; i += 2) {
        bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
    }
    return bytes;
}

/**
 * 将 Uint8Array 转换为十六进制字符串
 */
function bytesToHex(bytes) {
    return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * 从主密码派生加密密钥
 */
async function deriveKey(password, salt) {
    const encoder = new TextEncoder();
    const passwordKey = await window.crypto.subtle.importKey(
        "raw",
        encoder.encode(password),
        "PBKDF2",
        false,
        ["deriveKey"]
    );

    return await window.crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: ITERATIONS,
            hash: DIGEST
        },
        passwordKey,
        { name: "AES-GCM", length: KEY_LENGTH },
        false,
        ["encrypt", "decrypt"]
    );
}

/**
 * 加密数据
 * @param {string} text 要加密的文本 (通常是 JSON 字符串)
 * @param {string} password 主密码
 * @returns {Promise<string>} 格式: "salt_hex:iv_hex:ciphertext_hex"
 */
export async function encryptData(text, password) {
    const encoder = new TextEncoder();
    const salt = window.crypto.getRandomValues(new Uint8Array(16));
    const iv = window.crypto.getRandomValues(new Uint8Array(12));

    const key = await deriveKey(password, salt);

    const ciphertextBuffer = await window.crypto.subtle.encrypt(
        {
            name: "AES-GCM",
            iv: iv
        },
        key,
        encoder.encode(text)
    );

    return `${bytesToHex(salt)}:${bytesToHex(iv)}:${bytesToHex(new Uint8Array(ciphertextBuffer))}`;
}

/**
 * 解密数据
 * @param {string} encryptedString 格式为主密码加密后的字符串
 * @param {string} password 主密码
 * @returns {Promise<string>} 解密后的文本
 */
export async function decryptData(encryptedString, password) {
    try {
        const parts = encryptedString.split(':');
        if (parts.length !== 3) {
            throw new Error("Invalid encrypted data format");
        }

        const [saltHex, ivHex, ciphertextHex] = parts;
        const salt = hexToBytes(saltHex);
        const iv = hexToBytes(ivHex);
        const ciphertext = hexToBytes(ciphertextHex);

        const key = await deriveKey(password, salt);

        const decryptedBuffer = await window.crypto.subtle.decrypt(
            {
                name: "AES-GCM",
                iv: iv
            },
            key,
            ciphertext
        );

        const decoder = new TextDecoder();
        return decoder.decode(decryptedBuffer);
    } catch (error) {
        console.error("Decryption failed:", error);
        throw new Error("解密失败：主密码错误或数据已损坏");
    }
}
