def add_leading_zeros(number):
    """
    Ajoute deux zéros devant le nombre s'il est inférieur à 100.
    
    Args:
        number (int): Le nombre à traiter.
    
    Returns:
        str: Le nombre formaté avec deux zéros devant si nécessaire.
    """
    if number < 100:
        return f"{number:03d}"  # Format en ajoutant des zéros devant jusqu'à une longueur de 3 caractères
    return str(number)

# Exemple d'utilisation
print(add_leading_zeros(5))    # Résultat : "005"
print(add_leading_zeros(99))   # Résultat : "099"
print(add_leading_zeros(100))  # Résultat : "100"
print(add_leading_zeros(123))  # Résultat : "123"
