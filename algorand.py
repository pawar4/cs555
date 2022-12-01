import base64

from algosdk.future import transaction
from algosdk import mnemonic
from algosdk.v2client import algod
from pyteal import *
import algosdk

# user declared account mnemonics
benefactor_mnemonic = "magnet express worry phrase dismiss labor right program appear inside cube govern odor weapon knock flush pink glare rigid cheap settle debate iron abandon drink"
sender_mnemonic = "rally loyal price fashion disease rain zoo indicate until gentle ahead trap view observe index deer used space copper talent way old patient abandon simple"


# user declared algod connection parameters. Node must have EnableDeveloperAPI set to true in its config
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# helper function to compile program source
def compile_smart_signature(client, source_code):
    compile_response = client.compile(source_code)
    return compile_response['result'], compile_response['hash']

# helper function that converts a mnemonic passphrase into a private signing key
def get_private_key_from_mnemonic(mn) :
    private_key = mnemonic.to_private_key(mn)
    return private_key



def payment_transaction(creator_mnemonic, amt, rcv, algod_client)->dict:
    params = algod_client.suggested_params()
    add = mnemonic.to_public_key(creator_mnemonic)
    key = mnemonic.to_private_key(creator_mnemonic)
    unsigned_txn = transaction.PaymentTxn(add, params, rcv, amt)
    signed = unsigned_txn.sign(key)
    txid = algod_client.send_transaction(signed)
    pmtx = transaction.wait_for_confirmation(algod_client, txid , 5)
    return pmtx

def lsig_payment_txn(escrowProg, escrow_address, amt, rcv, algod_client):
    params = algod_client.suggested_params()
    unsigned_txn = transaction.PaymentTxn(escrow_address, params, rcv, amt)
    encodedProg = escrowProg.encode()
    program = base64.decodebytes(encodedProg)
    lsig = transaction.LogicSigAccount(program)
    stxn = transaction.LogicSigTransaction(unsigned_txn, lsig)
    tx_id = algod_client.send_transaction(stxn)
    pmtx = transaction.wait_for_confirmation(algod_client, tx_id, 10)
    return pmtx

"""Basic Donation Escrow"""

def donation_escrow(benefactor):

    #Only the benefactor account can withdraw from this escrow
    program = And(
        Txn.type_enum() == TxnType.Payment,
        Txn.receiver() == Addr(benefactor),
        Global.group_size() == Int(1),
        Txn.rekey_to() == Global.zero_address()
    )

    # Mode.Signature specifies that this is a smart signature
    return compileTeal(program, Mode.Signature, version=5)


def get_balance(m):
  algod_client = algod.AlgodClient(algod_token, algod_address)
  my_address = mnemonic.to_public_key(m)
  account_info = algod_client.account_info(my_address)
  return account_info.get('amount')
  

def send_money(sender_m, receiver_m):
  # initialize an algodClient
  algod_client = algod.AlgodClient(algod_token, algod_address)

  # define private keys
  receiver_public_key = mnemonic.to_public_key(receiver_m)

  stateless_program_teal = donation_escrow(receiver_public_key)
  escrow_result, escrow_address= compile_smart_signature(algod_client, stateless_program_teal)

  #print("Program:", escrow_result)
  #print("hash: ", escrow_address)

  # Activate escrow contract by sending 2 algo for transaction fee from creator
  amt = 10000 * 1000000
  payment_transaction(sender_m, amt, escrow_address, algod_client)


def receive_money(receiver_m):
  # initialize an algodClient
  algod_client = algod.AlgodClient(algod_token, algod_address)

  # define private keys
  receiver_public_key = mnemonic.to_public_key(receiver_m)

  stateless_program_teal = donation_escrow(receiver_public_key)
  escrow_result, escrow_address= compile_smart_signature(algod_client, stateless_program_teal)

  #print("Program:", escrow_result)
  #print("hash: ", escrow_address)

  # Withdraws 1 ALGO from smart signature using logic signature.
  withdrawal_amt = 10000 * 1000000
  lsig_payment_txn(escrow_result, escrow_address, withdrawal_amt, receiver_public_key, algod_client)

acc3 = "magnet express worry phrase dismiss labor right program appear inside cube govern odor weapon knock flush pink glare rigid cheap settle debate iron abandon drink"
acc2 = "rally loyal price fashion disease rain zoo indicate until gentle ahead trap view observe index deer used space copper talent way old patient abandon simple"
acc1 = "minimum law tackle eager asset energy true stove human sock comic autumn brass rib harsh mobile ivory inspire stool reopen deny repair spirit above imitate"

# send_money(acc2, acc3)
# receive_money(acc3)