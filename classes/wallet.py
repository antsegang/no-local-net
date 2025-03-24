import hashlib
import hmac
import secrets
import base64
from typing import Optional, Tuple
from coincurve import PrivateKey, PublicKey
from pydantic import Field, PrivateAttr
from utils.word_list import WORD_LIST
from eth_utils import keccak

# BIP-39
BIP39_WORDLIST = WORD_LIST
BIP39_STRENGTH = 128
PBKDF2_ROUNDS = 2048
HMAC_KEY = b'Bitcoin seed'
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

class Wallet:

    def __init__(self, mnemonic: Optional[str] = None, passphrase: str = "", account: int = 0, index: int = 0):
        # Public
        self.address: str = None
        self.public_key: bytes = None

        # Private
        self.__private_key: bytes = None
        self.__chain_code: bytes = None
        self.__mnemonic: str = None
        if self.__private_key is None or self.__chain_code is None or self.__mnemonic is None:
            self.__generate_hd_wallet(mnemonic, passphrase, account, index)

    def __generate_hd_wallet(self, mnemonic: Optional[str], passphrase: str, account: int, index: int):
        self.__mnemonic = mnemonic or self.__generate_bip39_mnemonic()
        seed = self.__derive_seed(passphrase)
        self.__private_key, self.__chain_code = self.__derive_master_key(seed)
        self.__derive_bip44_keys(account, index)
        self.address = self.__generate_eth_address()

    def get_recovery_key(self) -> str:
        recovery_key = base64.urlsafe_b64encode(self.__mnemonic.encode('utf-8')).decode('utf-8')

        return recovery_key
    
    @classmethod
    def from_recovery_key(cls, recovery_key: str, passphrase: str = ""):
        mnemonic = base64.urlsafe_b64decode(recovery_key.encode('utf-8')).decode('utf-8')

        wallet = cls(mnemonic=mnemonic, passphrase=passphrase)

        return wallet

    @staticmethod
    def __generate_bip39_mnemonic() -> str:
        entropy = secrets.token_bytes(BIP39_STRENGTH // 8)
        entropy_hash = hashlib.sha256(entropy).digest()
        checksum_bits = bin(int.from_bytes(entropy_hash, 'big'))[2:].zfill(256)[:BIP39_STRENGTH // 32]
        entropy_bits = bin(int.from_bytes(entropy, 'big'))[2:].zfill(BIP39_STRENGTH)
        bits = entropy_bits + checksum_bits
        return ' '.join([BIP39_WORDLIST[int(bits[i*11:(i+1)*11], 2)] for i in range(len(bits) // 11)])
    
    def __derive_seed(self, passphrase: str) -> bytes:
        return hashlib.pbkdf2_hmac(
            'sha512',
            self.__mnemonic.encode('utf-8'),
            salt=f'mnemonic{passphrase}'.encode('utf-8'),
            iterations=PBKDF2_ROUNDS
        )
    
    def __derive_master_key(self, seed: bytes) -> Tuple[bytes, bytes]:
        h = hmac.new(HMAC_KEY, seed, hashlib.sha512).digest()
        return h[:32], h[32:]
    
    def __derive_bip44_keys(self, account: int, index: int):
        hardened = 0x80000000
        path = [ 44 | hardened, 60 | hardened, account | hardened, 0, index]
        for depth, i in enumerate(path):
            self.__private_key, self.__chain_code = self.__cdk_priv(i)
        self.public_key = PrivateKey(self.__private_key).public_key.format(compressed=True)

    def __cdk_priv(self, index: int):
        data = b'\x00' + self.__private_key + index.to_bytes(4, 'big')
        h = hmac.new(self.__chain_code, data, hashlib.sha512).digest()
        child_private = (int.from_bytes(self.__private_key, 'big') + int.from_bytes(h[:32], 'big')) % SECP256K1_ORDER
        return child_private.to_bytes(32, 'big'), h[32:]
    
    def __generate_eth_address(self) -> str:
        keccak_hash = keccak(self.public_key[1:])
        address = keccak_hash[-20:].hex()
        return self.__checksum_address(address)
    
    @staticmethod
    def __checksum_address(address: str) -> str:
        addr_hash = keccak(address.lower().encode()).hex()
        return 'Φx' + ''.join(
            c.upper() if int(addr_hash[i], 16) > 7 else c
            for i, c in enumerate(address)
        )
    
    def sign_transaction(self, qtx_hash: str) -> Tuple[str,str,int]:
        if not qtx_hash:
            raise ValueError('Invalid transaction hash')
        hash_for_verification = qtx_hash.replace('Φx', '')
        privkey = PrivateKey(self.__private_key)
        signature = privkey.sign_recoverable(bytes.fromhex(hash_for_verification))
        r, s, v = self.split_signature(signature)
        return r.hex(), s.hex(), v + 27

    @staticmethod
    def split_signature(signature: bytes) -> Tuple[bytes,bytes,int]:
        if len(signature) != 65:
            raise ValueError('Incorrect signature len')
        r = signature[:32]
        s = signature[32:64]
        v = signature[64]

        return r, s, v
    
    def verify_signature(self, r: str, s: str, v: int, qtx_hash: str) -> bool:
        if not r or not s or not v or not qtx_hash:
            raise ValueError('Invalid signature or transaction hash')
        hash_for_verification = qtx_hash.replace('Φx', '')
        v = v - 27
        signature = bytes.fromhex(r) + bytes.fromhex(s) + bytes([v])
        pubkey = PublicKey.from_signature_and_message(signature, bytes.fromhex(hash_for_verification))
        print(f'pubkey: {pubkey.format().hex()}, public key: {self.public_key.hex()}')
        return pubkey.format() == self.public_key
    
    def export_private_key(self) -> str:
        return self.__private_key.hex()
    
    def get_public_info(self) -> dict:
        return {
            'address': self.address,
            'public_key': self.public_key.hex()
        }
    
    def wipe(self):
        self.__private_key = b'\x00' * 32
        self.__chain_code = b'\x00' * 32
        self.__mnemonic = 'x' * 99
        self.public_key = b'\x00' * 65
        self.address = 'Φx0000000000000000000000000000000000000000'