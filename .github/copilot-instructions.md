# GitHub Copilot – Pull Request Review Instructions

## 🎯 Rôle de Copilot dans les Pull Requests

Copilot **ne doit PAS** faire de review de code dans les Pull Requests.  
La review du code est la responsabilité des membres de l'équipe.

Copilot se concentre **uniquement** sur les points listés ci-dessous.

---

## ✅ Ce que Copilot doit vérifier

### 1. Orthographe et typographie
- Fautes d'orthographe dans les commentaires, docstrings, messages de commit, noms de variables, noms de fonctions, noms de fichiers.
- Fautes de frappe (typos) : lettres inversées, doublons, lettres manquantes.
- Majuscules manquantes en début de phrase dans les commentaires et docstrings.
- Ponctuation incorrecte ou manquante dans les commentaires.

### 2. Traduction et cohérence de langue
- Le projet doit être **entièrement en anglais** (commentaires, noms de variables, noms de fonctions, messages de commit, docstrings).
- Signaler tout commentaire, variable, ou message écrit en français ou dans une autre langue.
- Proposer une traduction anglaise correcte et naturelle.

### 3. Normalisation des noms (conventions de nommage)
- **Variables et fonctions** : `snake_case`
- **Classes** : `PascalCase`
- **Constantes** : `UPPER_SNAKE_CASE`
- **Fichiers** : `snake_case`
- Signaler tout nom qui ne respecte pas ces conventions et proposer une correction.

### 4. Cohérence des messages de commit
- Les messages de commit doivent être en **anglais**.
- Ils doivent suivre le format : `type: short description` (ex: `fix: correct typo in README`).
- Types acceptés : `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.
- Signaler les messages vagues comme `"fix"`, `"update"`, `"wip"`, `"test"` sans description.

### 5. Documentation et commentaires
- Les commentaires doivent être clairs, complets et grammaticalement corrects.
- Les docstrings doivent décrire ce que fait la fonction/classe (pas comment elle le fait).
- Signaler les commentaires vides, inutiles (`# loop`, `# here`) ou obsolètes.

---

## ❌ Ce que Copilot ne doit PAS faire

- ❌ Suggérer des refactorisations de code  
- ❌ Proposer des optimisations de performance  
- ❌ Commenter la logique ou l'architecture du code  
- ❌ Suggérer des bibliothèques alternatives  
- ❌ Faire des remarques sur la structure des fichiers ou des dossiers  
- ❌ Commenter les choix algorithmiques  

---

## 📝 Format des commentaires de Copilot

Chaque commentaire doit suivre ce format :

```text
🔥 [CATÉGORIE] – Courte description du problème

Avant : `<texte original>`
Après  : `<texte corrigé>`
