from abc import ABC, abstractmethod

# ==========================================
# PART 1: THE ABSTRACT CLASS
# ==========================================
class Character(ABC):
    def __init__(self, name, health):
        self.name = name
        self.health = health

    @abstractmethod
    def attack(self):
        pass

    @abstractmethod
    def special_skill(self):
        pass

# ==========================================
# PART 2: THE SUBCLASSES
# ==========================================

class GlitchEntity(Character):
    def __init__(self, name, health=150):
        # Using the oldest, safest super() format
        super(GlitchEntity, self).__init__(name, health)

    def attack(self):
        return "[" + self.name + "] slashes with corrupted static claws!"

    def special_skill(self):
        return "[" + self.name + "] uses Phase Dash to teleport behind the enemy!"

class CyberKnight(Character):
    def __init__(self, name, health=250):
        super(CyberKnight, self).__init__(name, health)

    def attack(self):
        return "[" + self.name + "] swings a neon broadsword!"

    def special_skill(self):
        return "[" + self.name + "] deploys Aegis Protocol for invulnerability!"

# ==========================================
# PART 3: EXECUTION AND OUTPUT
# ==========================================

# Instantiate the characters
my_wraith = GlitchEntity("Null")
my_knight = CyberKnight("Sir Lancer")

# Print the results using basic string concatenation
print("--- CHARACTER 1 ---")
print("Name: " + my_wraith.name)
print("Health: " + str(my_wraith.health))
print("Attack: " + my_wraith.attack())
print("Skill: " + my_wraith.special_skill())

print("\n-------------------\n")

print("--- CHARACTER 2 ---")
print("Name: " + my_knight.name)
print("Health: " + str(my_knight.health))
print("Attack: " + my_knight.attack())
print("Skill: " + my_knight.special_skill())
