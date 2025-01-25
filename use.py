from encryption_utils import generate_key_pair,save_private_key,save_public_key
private_key, public_key = generate_key_pair()
save_private_key(private_key, 'private_key.pem')
save_public_key(public_key, 'public_key.pem')