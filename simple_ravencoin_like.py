#!/usr/bin/env python3
"""
نظام بلوكتشين مبسط مماثل لـ Ravencoin
- نظام نقل الأصول (Tokens)
- تشفير التجزئة
- بروتوكول PoW بسيط
- نظام محفظة بسيط
"""

import hashlib
import json
import time
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transaction:
    """تمثيل المعاملات"""
    sender: str
    recipient: str
    amount: float
    asset_name: str = "RVN"  # اسم الأصل (مثل RVN في Ravencoin)
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'asset_name': self.asset_name,
            'timestamp': self.timestamp
        }
    
    def hash(self) -> str:
        """حساب تجزئة المعاملة"""
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True).encode()).hexdigest()


@dataclass
class Block:
    """تمثيل الكتلة"""
    index: int
    transactions: List[Transaction]
    timestamp: float
    previous_hash: str
    nonce: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'index': self.index,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }
    
    def hash(self) -> str:
        """حساب تجزئة الكتلة"""
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True).encode()).hexdigest()


class SimpleAssetBlockchain:
    """نظام بلوكتشين بسيط مماثل لـ Ravencoin مع دعم الأصول"""
    
    def __init__(self):
        self.chain: List[Block] = []
        self.current_transactions: List[Transaction] = []
        self.difficulty = 4  # عدد الأصفار في بداية التجزئة
        self.mining_reward = 50  # مكافأة التعدين
        
        # إنشاء الكتلة الجذرية (Genesis Block)
        self.create_genesis_block()
        
        # نظام الأصول - تتبع إصدار الأصول
        self.assets: Dict[str, Dict[str, Any]] = {}
    
    def create_genesis_block(self):
        """إنشاء الكتلة الجذرية"""
        genesis_block = Block(
            index=0,
            transactions=[],
            timestamp=time.time(),
            previous_hash="0"
        )
        
        # إنشاء تجزئة صحيحة للكتلة الجذرية
        while not self.is_valid_proof(genesis_block):
            genesis_block.nonce += 1
        
        self.chain.append(genesis_block)
    
    def is_valid_proof(self, block: Block) -> bool:
        """التحقق مما إذا كانت تجزئة الكتلة تبدأ بعدد معين من الأصفار"""
        block_hash = block.hash()
        return block_hash[:self.difficulty] == '0' * self.difficulty
    
    def proof_of_work(self, block: Block) -> int:
        """خوارزمية إثبات العمل - العثور على nonce الصحيح"""
        block.nonce = 0
        while not self.is_valid_proof(block):
            block.nonce += 1
        return block.nonce
    
    def new_block(self, previous_hash: str = None) -> Block:
        """إنشاء كتلة جديدة"""
        if previous_hash is None:
            previous_hash = self.chain[-1].hash()
        
        block = Block(
            index=len(self.chain),
            transactions=self.current_transactions,
            timestamp=time.time(),
            previous_hash=previous_hash
        )
        
        # إيجاد nonce الصحيح باستخدام PoW
        self.proof_of_work(block)
        
        # إعادة تعيين قائمة المعاملات الحالية
        self.current_transactions = []
        
        self.chain.append(block)
        return block
    
    def new_transaction(self, sender: str, recipient: str, amount: float, asset_name: str = "RVN") -> int:
        """إضافة معاملة جديدة"""
        transaction = Transaction(
            sender=sender,
            recipient=recipient,
            amount=amount,
            asset_name=asset_name
        )
        self.current_transactions.append(transaction)
        return self.last_block.index + 1
    
    def issue_asset(self, issuer: str, asset_name: str, quantity: int, units: int = 0, has_ipfs: bool = False, ipfs_hash: str = None) -> bool:
        """إصدار أصل جديد (مثل نظام الأصول في Ravencoin)"""
        if asset_name in self.assets:
            print(f"خطأ: الأصل {asset_name} موجود بالفعل")
            return False
        
        self.assets[asset_name] = {
            'issuer': issuer,
            'quantity': quantity,
            'units': units,
            'has_ipfs': has_ipfs,
            'ipfs_hash': ipfs_hash,
            'created_at': time.time()
        }
        
        # إضافة معاملة إصدار الأصل
        self.new_transaction(
            sender=issuer,
            recipient=issuer,
            amount=quantity,
            asset_name=asset_name
        )
        
        print(f"تم إصدار الأصل {asset_name} بنجاح")
        return True
    
    @property
    def last_block(self) -> Block:
        """الحصول على آخر كتلة في السلسلة"""
        return self.chain[-1]
    
    def get_balance(self, address: str, asset_name: str = "RVN") -> float:
        """الحصول على رصيد عنوان معين لAsset معين"""
        balance = 0.0
        
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.recipient == address and transaction.asset_name == asset_name:
                    balance += transaction.amount
                if transaction.sender == address and transaction.asset_name == asset_name:
                    balance -= transaction.amount
        
        return balance
    
    def is_chain_valid(self) -> bool:
        """التحقق من صحة السلسلة"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # التحقق من التجزئة
            if current_block.previous_hash != previous_block.hash():
                print(f"خطأ: تجزئة الكتلة {i} لا تتطابق")
                return False
            
            # التحقق من صحة PoW
            if not self.is_valid_proof(current_block):
                print(f"خطأ: إثبات العمل للكتلة {i} غير صحيح")
                return False
        
        return True


def demonstrate_simple_ravencoin():
    """عرض توضيحي لنظام البلوكتشين المبسط"""
    print("=== نظام بلوكتشين مبسط مماثل لـ Ravencoin ===\n")
    
    # إنشاء سلسلة بلوكتشين جديدة
    blockchain = SimpleAssetBlockchain()
    
    print("1. تم إنشاء السلسلة مع الكتلة الجذرية")
    print(f"   عدد الكتل: {len(blockchain.chain)}")
    
    # إصدار أصل جديد (مثل نظام الأصول في Ravencoin)
    print("\n2. إصدار أصل جديد:")
    blockchain.issue_asset(
        issuer="RAddress123456789",
        asset_name="MYTOKEN",
        quantity=1000,
        units=0,
        has_ipfs=True,
        ipfs_hash="QmXoypizjW3WknFiJnKLwL7Q19drKo1q..."
    )
    
    # إضافة بعض المعاملات
    print("\n3. إضافة معاملات:")
    blockchain.new_transaction(
        sender="RAddress123456789",
        recipient="RAddress987654321",
        amount=100,
        asset_name="MYTOKEN"
    )
    
    blockchain.new_transaction(
        sender="RAddress123456789",
        recipient="RAddress555555555",
        amount=50,
        asset_name="MYTOKEN"
    )
    
    # تعدين الكتلة التالية
    print("\n4. تعدين كتلة جديدة...")
    previous_hash = blockchain.last_block.hash()
    new_block = blockchain.new_block(previous_hash)
    print(f"   تم إنشاء الكتلة {new_block.index} مع تجزئة: {new_block.hash()[:10]}...")
    
    # عرض معلومات السلسلة
    print(f"\n5. معلومات السلسلة:")
    print(f"   عدد الكتل: {len(blockchain.chain)}")
    print(f"   صحة السلسلة: {'صحيحة' if blockchain.is_chain_valid() else 'غير صحيحة'}")
    
    # عرض الأصول الصادرة
    print(f"\n6. الأصول الصادرة:")
    for asset_name, asset_info in blockchain.assets.items():
        print(f"   - {asset_name}: {asset_info['quantity']} وحدة، المصدر: {asset_info['issuer']}")
    
    # عرض الأرصدة
    print(f"\n7. الأرصدة:")
    print(f"   رصيد RAddress123456789 لـ MYTOKEN: {blockchain.get_balance('RAddress123456789', 'MYTOKEN')}")
    print(f"   رصيد RAddress987654321 لـ MYTOKEN: {blockchain.get_balance('RAddress987654321', 'MYTOKEN')}")
    print(f"   رصيد RAddress555555555 لـ MYTOKEN: {blockchain.get_balance('RAddress555555555', 'MYTOKEN')}")
    
    # عرض محتوى الكتل
    print(f"\n8. محتوى الكتل:")
    for i, block in enumerate(blockchain.chain):
        print(f"   كتلة {i}:")
        print(f"     تجزئة: {block.hash()[:10]}...")
        print(f"     عدد المعاملات: {len(block.transactions)}")
        for j, tx in enumerate(block.transactions):
            print(f"       معاملة {j+1}: {tx.sender} -> {tx.recipient} ({tx.amount} {tx.asset_name})")


if __name__ == "__main__":
    demonstrate_simple_ravencoin()