# Résumé Architectural : Système de Droits d'Accès Granulaire et Infrastructure d'Annulation (Soft Delete)

Ce document présente l'architecture technique complète mise en place pour la gestion des droits d'accès granulaires (RBAC) et l'annulation logique des données dans l'application Django.

---

## 1. Architecture du Système de Contrôle d'Accès (RBAC)

Le système de droits d'accès a été conçu pour permettre une configuration fine des permissions par utilisateur, par service et par sous-onglet (module), gérée en temps réel par les administrateurs.

### A. Modèle de Données : `DroitAcces`
Défini dans [apps/gestion_droits_acces/models.py](file:///c:/Users/PC/Downloads/projet%20stage/projet%20stage/labocos/apps/gestion_droits_acces/models.py).
Chaque enregistrement associe un **utilisateur** à un **service** (ex: *Service Administratif*, *Service Technique*) et un **module/sous-onglet** (ex: *devis*, *dossier*, *fiche_qualification*) avec 4 permissions booléennes :
- `peut_voir` : Droit d'affichage de la liste et du détail.
- `peut_ajouter` : Droit de création d'un nouvel enregistrement.
- `peut_modifier` : Droit d'édition.
- `peut_annuler` : Droit d'annulation logique et de restauration, ainsi que la visibilité des lignes annulées.

### B. Couche de Sécurité Applicative

1. **Middleware de Sélection de Service (`ServiceSelectionMiddleware`)** :
   - Défini dans [apps/core/middleware.py](file:///c:/Users/PC/Downloads/projet%20stage/projet%20stage/labocos/apps/core/middleware.py).
   - Intercepte les requêtes des utilisateurs connectés (hors superutilisateurs/admin) et vérifie s'ils ont sélectionné un service actif en session (`selected_service`).
   - Si un utilisateur a accès à un seul service, celui-ci est sélectionné par défaut. S'il n'a accès à aucun ou à plusieurs, il est redirigé vers l'écran de sélection de service (`core:select_service`).

2. **Mixin de Permission de Vue (`ModulePermissionMixin`)** :
   - Défini dans [apps/core/mixins.py](file:///c:/Users/PC/Downloads/projet%20stage/projet%20stage/labocos/apps/core/mixins.py).
   - Utilisé par toutes les vues de l'application. Il surcharge `dispatch()` pour interdire l'accès en fonction de la permission requise (`action_name`) et du sous-onglet (`module_name`).
   - Surcharge `get_queryset()` : Si l'utilisateur n'a pas la permission `peut_voir` (mais possède par exemple uniquement la permission `peut_ajouter`), la vue renvoie un queryset vide (`qs.none()`), empêchant toute fuite de données au niveau ORM.

3. **Matrice d'Administration Temps Réel** :
   - Définie dans [apps/gestion_droits_acces/views.py](file:///c:/Users/PC/Downloads/projet%20stage/projet%20stage/labocos/apps/gestion_droits_acces/views.py).
   - Permet aux superutilisateurs de configurer les droits en session via une grille interactive.
   - Les modifications sont enregistrées instantanément en base de données à l'aide de requêtes **AJAX (fetch POST)**, évitant ainsi le rechargement de la page.

---

## 2. Infrastructure d'Annulation Logique (Soft Delete)

L'annulation logique permet de masquer les données supprimées des flux de travail quotidiens tout en conservant une trace historique et en offrant la possibilité de les restaurer.

### A. Modèle de Base et Managers : `BaseModel`
Défini dans `apps/core/models.py`.
Tous les modèles métiers (Client, Devis, Dossier, Convention, BL, etc.) héritent de `BaseModel` :
- **Champs d'annulation** :
  - `est_annule` (Boolean) : Indique si l'objet est annulé.
  - `annule_le` (DateTimeField) : Date et heure de l'annulation.
  - `annule_par` (ForeignKey vers User) : Utilisateur ayant réalisé l'annulation.
- **Managers de requêtes** :
  - `objects` (Manager par défaut) : Filtre automatiquement pour ne retourner que les objets actifs (`est_annule=False`).
  - `objects_all` (Manager complet) : Retourne tous les objets, y compris ceux qui sont annulés.

### B. Vues Génériques d'Annulation/Restauration
Définies dans `apps/commercial/views.py`.
- **`AnnulerView`** : Reçoit une requête `POST`, marque l'objet comme annulé (`est_annule=True`), enregistre l'utilisateur et la date, consigne l'action dans l'**Audit Log** du système, puis redirige avec un message de succès.
- **`RestaurerView`** : Reçoit une requête `POST`, restaure l'objet (`est_annule=False`), consigne l'action dans l'Audit Log, puis redirige.

### C. Gestion des Droits et Filtrage dans les Templates

Toutes les listes clés du module Commercial disposent désormais d'une intégration complète :
- Le bouton **"Voir annulés" / "Masquer annulés"** est masqué par défaut et n'apparaît que si l'utilisateur possède la permission `peut_annuler`.
- Le filtrage en base de données vérifie cette permission : si un utilisateur injecte manuellement le paramètre `?afficher_annules=1` dans l'URL sans en avoir le droit, la vue filtre uniquement les objets actifs.
- Des boutons interactifs permettent d'annuler ou de restaurer l'élément directement à partir de la ligne de tableau.

---

## 3. Cartographie des Sous-onglets de l'Application

Les permissions sont associées aux identifiants uniques de sous-onglets ci-dessous, mappés dynamiquement via la propriété `module_name` de chaque vue :

| Service | Module / Vue | Permission ID (`module_name`) |
| :--- | :--- | :--- |
| **Administratif** | Clients | `client` |
| | Revue de la Demande | `revue_demande` |
| | Devis | `devis` |
| | Dossiers | `dossier` |
| | Conventions | `convention` |
| | Bons de Livraison | `bon_livraison` |
| | AO Soumission | `ao_soumission` |
| | AO Adjugé | `ao_adjuge` |
| | Cautions | `caution` |
| | Décomptes | `decompte` |
| | Résultats BC | `resultat_bc` |
| | Factures | `facture` |
| | Encaissements | `encaissement` |
| | Recouvrements | `recouvrement` |
| | Caisse | `mouvement_caisse` |
| | Achats (bci, demande_prix, etc.) | *Dynamique en fonction du paramètre `?tab=`* |
| | Ressources Humaines (personnel, conges, etc.) | *Dynamique en fonction du paramètre `?tab=`* |
| **Technique** | Réception | *Dynamique en fonction du paramètre `?tab=`* (`reception_feuilles`, `reception_planning`) |
| | Labo (préparation, solution, balances, etc.) | *Dynamique en fonction du paramètre `?tab=`* |
| | Formation (fiche_qualification, etc.) | *Dynamique en fonction du paramètre `?tab=`* |
| **Qualité** | GED (suivi_docs, liste_suivi, etc.) | *Dynamique en fonction du paramètre `?tab=`* |
| | Fiche de Progrès | `fiche_progres` |
| **Métrologie** | Inventaire, Fiche de Vie, Plannings, etc. | *Associe individuellement chaque sous-onglet* |
