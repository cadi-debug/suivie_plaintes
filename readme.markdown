
---

### Fichier : `README.md`

Copie ce contenu à la racine de ton projet.

```markdown
# 🏛️ SGP Justice RDC - Système de Gestion des Plaintes

Une application Web & Mobile (PWA) permettant la digitalisation du processus de dépôt et de suivi des plaintes judiciaires en République Démocratique du Congo.

## 📋 Fonctionnalités Clés

* **Public (Citoyen) :**
    * Suivi de dossier en temps réel via un graphe interactif (D3.js).
    * Recherche par scan QR Code (PWA) ou référence unique.
    * Confidentialité : Aucune donnée sensible n'est exposée publiquement.
* **Privé (Greffe & Parquet) :**
    * Dashboard de gestion des plaintes.
    * Workflow dynamique (Dépôt -> Recevabilité -> Audience -> Jugement).
    * Génération de Récépissés PDF avec QR Code.
    * Gestion des pièces à conviction (Numériques et Physiques).
    * Historique inaltérable des actions.

---

## 🛠️ Prérequis techniques

* Python 3.10+
* Pip (Gestionnaire de paquets)
* Virtualenv (Recommandé)

---

## 🚀 Installation & Configuration

### 1. Cloner le projet
Récupérez le code source (les migrations sont déjà incluses dans le dépôt).

```bash
git clone <votre-repo-url>
cd suivie_plaintes

```

### 2. Créer l'environnement virtuel

Il est crucial d'isoler les dépendances du projet.

**Sous Windows :**

```bash
python -m venv env
.\env\Scripts\activate

```

**Sous Mac/Linux :**

```bash
python3 -m venv env
source env/bin/activate

```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt

```

### 4. Base de Données & Migrations

Les fichiers de migration étant suivis par Git, il suffit d'appliquer le schéma à votre base de données locale (SQLite par défaut).

```bash
python manage.py migrate

```

---

## 🌱 Initialisation des Données (Peupler la DB)

Pour utiliser l'application, vous avez besoin des groupes utilisateurs (Greffier, Procureur) et d'un compte administrateur.

1. Assurez-vous d'avoir le script `init_db.py` à la racine (voir section Scripts ci-dessous).
2. Lancez la commande suivante dans le shell Django :

```bash
# Lancez le shell
python manage.py shell

# Dans le shell interactif python, tapez :
>>> import init_db
>>> exit()

```

Cela va créer automatiquement :

* Un super-administrateur.
* Un compte **Greffier**.
* Un compte **Procureur**.
* Les groupes de permissions nécessaires.

### 🔑 Identifiants par défaut (Générés par le script)

| Rôle | Nom d'utilisateur | Mot de passe |
| --- | --- | --- |
| **Super Admin** | `admin` | `admin123` |
| **Greffier** | `greffier` | `justice2026` |
| **Procureur** | `procureur` | `loi2026` |

---

## ▶️ Lancer le projet

```bash
python manage.py runserver

```

* **Accueil Public (Scan/Recherche) :** [http://127.0.0.1:8000/](https://www.google.com/search?q=http://127.0.0.1:8000/)
* **Connexion Agents :** [http://127.0.0.1:8000/accounts/login/](https://www.google.com/search?q=http://127.0.0.1:8000/accounts/login/)

---

## 📱 Tester la PWA (Mobile)

Pour tester le scanner QR Code et l'installation sur mobile :

1. Votre téléphone et votre PC doivent être sur le même réseau Wifi.
2. Lancez le serveur en écoutant sur toutes les IPs : `python manage.py runserver 0.0.0.0:8000`.
3. Sur le téléphone, accédez à `http://<IP_DE_VOTRE_PC>:8000`.
4. **Note :** Le scanner QR Code nécessite un contexte sécurisé (HTTPS). En local, certains navigateurs bloquent la caméra si ce n'est pas `localhost`. Pour tester pleinement la caméra, utilisez le navigateur de votre PC ou configurez un tunnel (ex: Ngrok).

---

## 📂 Structure des Dossiers Importants

* `dossiers/` : Gestion des plaintes, pièces à conviction et PDF.
* `workflow/` : Logique métier, étapes de la procédure et API du Graphe D3.js.
* `templates/` : Fichiers HTML (Tailwind CSS via CDN).
* `static/` : Images (Logo), JS (Service Worker), CSS.
* `media/` : Stockage des pièces jointes (non suivi par Git).

---

## ⚠️ Dépannage Courant

**Erreur `CSRF verification failed` :**
Assurez-vous d'accéder au site via l'adresse configurée dans `ALLOWED_HOSTS`. En développement, `127.0.0.1` est sûr.

**Erreur lors de l'upload de fichiers :**
Vérifiez que le dossier `media/` existe à la racine et que vous avez les droits d'écriture dessus.

**Le graphe ne s'affiche pas :**
Vérifiez la console du navigateur (F12). Si le JSON renvoie une erreur 500, vérifiez que la plainte a bien une étape initiale créée.

```

---

### Fichier : `init_db.py` (Script de peuplement)

Crée ce fichier à la racine de ton projet (au même niveau que `manage.py`). Il servira à configurer l'environnement en une seconde.

```python
import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ton_projet.settings') # <--- REMPLACE 'ton_projet' par le nom de ton dossier settings
django.setup()

from django.contrib.auth.models import User, Group, Permission
from dossiers.models import Plainte # Vérification que les models chargent bien

def init():
    print("🚀 Démarrage de l'initialisation de la Base de Données...")

    # 1. Création du SuperUser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@justice.cd', 'admin123')
        print("✅ Superuser 'admin' créé (Pass: admin123)")
    else:
        print("ℹ️ Superuser 'admin' existe déjà.")

    # 2. Création des Groupes
    groupe_greffier, created = Group.objects.get_or_create(name='Greffier')
    groupe_procureur, created = Group.objects.get_or_create(name='Procureur')
    print("✅ Groupes 'Greffier' et 'Procureur' vérifiés.")

    # 3. Création des Utilisateurs de test
    # Greffier
    if not User.objects.filter(username='greffier').exists():
        u = User.objects.create_user('greffier', 'greffier@justice.cd', 'justice2026')
        u.first_name = "Jean"
        u.last_name = "Kabila"
        u.groups.add(groupe_greffier)
        u.save()
        print("✅ Utilisateur 'greffier' créé (Pass: justice2026)")

    # Procureur
    if not User.objects.filter(username='procureur').exists():
        u = User.objects.create_user('procureur', 'procureur@justice.cd', 'loi2026')
        u.first_name = "Marie"
        u.last_name = "Tshilombo"
        u.groups.add(groupe_procureur)
        u.is_staff = True # Donne accès à l'admin panel éventuellement
        u.save()
        print("✅ Utilisateur 'procureur' créé (Pass: loi2026)")

    print("\n🎉 Initialisation terminée avec succès !")
    print("Vous pouvez lancer le serveur : python manage.py runserver")

if __name__ == '__main__':
    init()

```

### Fichier : `requirements.txt`

Si tu ne l'as pas encore généré, voici ce qu'il doit contenir au minimum vu ce qu'on a codé :

```text
asgiref==3.11.1
Django==6.0.2
pillow==12.1.0
sqlparse==0.5.5
tzdata==2025.3

```

Tu peux générer le tien exactement avec la commande : `pip freeze > requirements.txt`.