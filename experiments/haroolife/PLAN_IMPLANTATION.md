# HarooLife — plan d’implantation dans FaîtiereHub

Date : 10 octobre 2026. Statut : proposition d’architecture et de livraison, pas une fonctionnalité déployée.

## 1. Résultat recherché

Depuis FaîtiereHub, un producteur ou sa coopérative regroupe des travaux, des ouvriers constituent une équipe, les parties conviennent des conditions, puis suivent le chantier. HarooLife rend ce parcours visible et interactif. Chaque action métier reste utilisable dans une interface légère, sans déplacement d’avatar obligatoire.

Premier pilote proposé : une coopérative, un canton, une activité de récolte, des équipes réelles et des parcelles autorisées. Les valeurs 8 ouvriers, 10 hectares et 48 heures sont des paramètres hérités à confirmer avec le pilote, pas des règles agronomiques universelles.

## 2. Constats vérifiés dans les dépôts

| Élément | Existant inspecté | Conséquence |
|---|---|---|
| Identité FaîtiereHub | `Saas/lib/account/journey.ts`, `types/domain.ts` : rôle organisationnel et un type Haroo sur un même compte | Réutiliser les comptes ; ne pas inventer un rôle « joueur » donnant des permissions |
| Inscription | `Saas/app/auth/signup/page.tsx` : opérateur ou professionnel Haroo | Préserver ces parcours et conserver l’intention HarooLife jusqu’à leur fin |
| Opérateurs | `Saas/app/operator/page.tsx`, migrations partenaires : certification et mandats | L’accompagnement dépend des mandats ; certification et organisation ne sont pas des récompenses de jeu |
| Membres par carte | `Saas/lib/security/card-access.ts` : compte ou session de carte FAITIERE après code SMS | Un producteur peut utiliser les services sans compte Supabase classique ; le QR public seul n’autorise pas les actions |
| Professions Haroo | `Saas/app/api/account/activate-haroo/route.ts` | Un profil Haroo à la fois ; un membre peut aussi être ouvrier ; chercher des ouvriers ne nécessite pas de devenir ouvrier |
| Inscriptions Haroo intégrées | `Saas/app/api/haroo/auth/register/route.ts` → `agritogo/app/haroo/auth.py` | Le parcours intégré crée des identités dans Supabase |
| Haroo Django | `haroo/apps/users/authentication.py`, `haroo/haroo/settings/base.py` | Identités et JWT Django distincts : pas de connexion automatique avec Supabase démontrée |
| Recherche collective | `haroo/apps/jobs/models.py`, `views.py`, `serializers.py` | Logique 10 ha / 8 personnes présente mais parcours incohérent |
| Marché intégré | `Saas/app/api/market/announcements/route.ts`, routes d’annonces par carte | Les annonces `producer_announcements` et les offres `haroo_jobs` ne constituent pas déjà un moteur de recrutement collectif |
| Formation et conseil | Routes Academy et professionnels, `Saas/app/api/haroo/missions/*` | Réutiliser les services selon leurs autorisations ; ne pas confondre mission de conseil et contrat ouvrier |
| AgriTogo | API Flask, Supabase partagé, météo et outils IA/ML | Aide facultative au chantier, sans dépendance IA pour rejoindre ou confirmer une mission |
| TogoLife | `togolife/src/main.js`, `simulation.js` : scène Three.js et sauvegarde localStorage | Réutiliser rendu/avatar/interactions ; les sauvegardes locales ne sont pas une preuve d’engagement ou de revenu |

Les sources ont été inspectées localement. L’état réellement déployé, les migrations appliquées, les volumes Django et l’expérience mobile réelle n’ont pas été vérifiés par cette étude. Les commentaires et anciens audits ne remplacent pas les gardes et routes actuelles.

## 3. Défauts métier à résoudre avant intégration

- Les annonces ouvrières collectives démarrent en `ACTIVE` alors que rejoindre exige `EN_ATTENTE`.
- À 8 membres elles deviennent `VALIDEE`, mais la liste serveur ne retourne que `ACTIVE`.
- L’expiration automatique inspectée ne couvre que les annonces ouvrières `ACTIVE` ; l’action rejoindre ne contrôle pas explicitement la date d’expiration.
- La fonction frontend de participation à une équipe est définie/importée sans appel dans les écrans inspectés.
- L’action rejoindre un regroupement d’exploitants ne vérifie pas explicitement la règle annoncée de même zone.
- L’agrégation reprend la superficie totale du profil, au lieu d’une surface effectivement engagée pour ce chantier. Elle peut donc surévaluer le besoin ou compter deux fois une parcelle.
- Les actions de participation et de candidature doivent être protégées contre les appels simultanés : les transactions actuelles ne verrouillent pas les compteurs lus.
- L’action `postuler` crée directement un contrat `SIGNE` : cela ne démontre pas un accord explicite des deux parties.
- Le formulaire ouvrier affiche 1 000 FCFA/h, puis partage un montant journalier entre huit membres. Il faut décider si le tarif est par personne ou par équipe avant tout calcul financier.
- Les droits de modification/suppression des annonces doivent être audités au niveau du propriétaire ; être du même métier ne suffit pas.

Ces défauts sont des constats de code, pas des incidents de production reproduits. Ils doivent devenir des cas de test dans l’implémentation retenue.

## 4. Architecture recommandée

### Décision proposée

Intégrer le produit utilisateur dans **Saas**, sous une future route `/haroolife`, et créer le domaine de regroupement dans **Supabase**. Reprendre les règles utiles de Haroo Django et les corriger ; ne pas rendre la première version dépendante d’une seconde authentification Django.

- `Saas/app/haroolife/` : accueil contextualisé, vue légère et chargement optionnel de la scène.
- `Saas/components/haroolife/` : équipes, parcelles stylisées, propositions, confirmations, journal du chantier.
- `Saas/lib/haroolife/` : règles et contrats de données, indépendants du rendu.
- `Saas/app/api/haroolife/` : accès serveur, commandes et lectures limitées au périmètre autorisé.
- `Saas/supabase/migrations/` : modèle additif, politiques RLS et transitions transactionnelles.
- `haroo/experiments/haroolife/togolife/` : référence conservée ; extraire uniquement les éléments nécessaires à l’intégration, avec licences.
- AgriTogo : enrichissement météo/conseil ultérieur, sans autorité sur les engagements.

Le navigateur soumet des intentions. Le serveur relit identité, capacité et état métier, puis confirme la transition. Le rendu n’incrémente jamais directement une superficie, un effectif ou un revenu réel.

Si Haroo Django contient des utilisateurs ou contrats actifs à conserver, le lot 0 doit en mesurer le volume. Prévoir alors un import contrôlé avec identifiants externes uniques, rapprochement des identités et validation utilisateur ; ne pas joindre les personnes sur le seul numéro de téléphone ni activer une double écriture automatique. Les contraintes contractuelles peuvent conduire à revoir cette décision avant développement métier.

## 5. Parcours depuis l’écosystème

### Entrées

| Entrée | Action proposée |
|---|---|
| Accueil / visiteur | Découvrir une démonstration clairement identifiée ; s’identifier pour toute action réelle |
| `/haroo` / ouvrier | Reprendre son équipe, déclarer sa disponibilité, examiner une proposition |
| `/dashboard` / membre producteur | Organiser des travaux pour ses parcelles et rejoindre un regroupement |
| `/dashboard` / administrateur | Préparer des regroupements dans son périmètre ; recueillir la confirmation de chaque membre |
| Carte membre après accès privé | Parcours léger « Mes travaux », limité au membre identifié par la session de carte |
| `/operator` | Assistance et suivi permis par le mandat, avec trace de l’auteur ; pas d’engagement à la place d’un membre sans autorisation définie |
| Marché / annonce | Consulter la projection du chantier puis accéder au détail autorisé |
| Haroo / conseiller | Missions de conseil séparées des candidatures ouvrières |

Pour un compte connu : préremplir uniquement les données accessibles et demander les informations manquantes. Pour une session de carte : conserver le rattachement au membre, sans fabriquer un compte ni accorder un profil ouvrier. Un ouvrier utilise son compte professionnel dans le MVP. Les entrées acheteur, Academy et conseil seront reliées après validation de la boucle travail.

### Expérience interactive

- Maison de la coopérative : périmètre organisationnel et besoins à confirmer.
- Parcelles stylisées : travaux demandés, surface engagée, calendrier et regroupement.
- Maison des équipes : places libres, compétences et disponibilités.
- Tableau des propositions : explication du rapprochement et conditions proposées.
- Carnet de chantier : accords, planning, heures, validations et contestations.

La progression représente des actions confirmées : « 5/8 membres », « 7/10 ha », « 6 accords reçus ». La présence d’un avatar ne signifie pas que la personne est en ligne ou physiquement sur place. Pas de fausse présence multijoueur. Chaque lieu possède aussi un bouton accessible sans explorer la scène.

## 6. Données et règles du MVP

Noms de tables indicatifs ; réutiliser les entités existantes lorsque leur sémantique et leurs droits conviennent.

| Objet | Contenu essentiel |
|---|---|
| Besoin de travail | Membre, organisation, parcelle, surface engagée, travail, dates, effectif/heures estimés, unité du tarif |
| Regroupement | Zone, activité, créneau, seuil configurable, échéance, état |
| Contribution | Besoin et surface confirmée, auteur, date, retrait éventuel ; unicité empêchant le double comptage |
| Équipe | Responsable, capacité cible configurable, zone et état |
| Participation | Profil ouvrier, invitation/acceptation/retrait, compétences et dates ; une ligne par personne |
| Proposition | Équipe et chantier, motifs de compatibilité, conditions versionnées et expiration |
| Accord individuel | Acceptation de chaque ouvrier et du responsable du chantier ; pas de signature implicite à la candidature |
| Journal du travail | Heures par personne et date, validation ou contestation, historique |
| Événement métier | Acteur compte ou membre par carte, action, entité, version, clé d’idempotence |

Un acteur serveur distingue l’utilisateur connecté, le titulaire membre par carte et l’accompagnant mandaté. Les identifiants d’auteur et d’organisation ne sont jamais acceptés du client sans résolution et contrôle. Aucun rapprochement automatique compte/membre par nom ou téléphone.

Transitions proposées :

- Regroupement : `BROUILLON → OUVERT → PRET → ENGAGE → TERMINE`, avec `EXPIRE` et `ANNULE`.
- Équipe : `EN_CONSTITUTION → PRETE`, avec retrait pouvant remettre l’équipe en constitution avant engagement.
- Proposition : `PROPOSEE → ACCORDS_EN_COURS → CONFIRMEE`, ou `REFUSEE / EXPIREE`.
- Travail : `PLANIFIE → EN_COURS → A_VALIDER → VALIDE`, ou `CONTESTE`.

Un groupe complet n’engage personne automatiquement. Une modification du tarif, des dates ou du périmètre après acceptation crée une nouvelle version à accepter. Après engagement, un retrait suit une procédure de remplacement/annulation traçable. La fermeture d’un groupe n’efface pas son historique.

Les 10 hectares sont un seuil de regroupement, pas un calcul de charge. L’effectif dépend du travail et de la durée. Le rapprochement initial utilise des filtres déterministes : zone/mobilité, compétences, dates, capacité et conditions. Chaque suggestion indique pourquoi elle convient ; aucun appel LLM requis. Confirmer atomiquement la disponibilité pour éviter deux engagements incompatibles.

Échéances calculées avec l’heure serveur, affichées dans le contexte local. Refuser les nouvelles adhésions après échéance même si le traitement de nettoyage n’a pas encore tourné.

## 7. Protection et continuité

- RLS pour les comptes ; résolution serveur stricte pour les sessions de carte utilisant un client privilégié. Ne pas supposer que ces sessions fournissent `auth.uid()`.
- Relire la validité de la carte et les mandats. Le QR public donne accès à une fiche publique, pas au chantier privé.
- Membres : leurs propres données ; administrateurs : leur hiérarchie ; partenaires : capacités mandatées. Le partage d’un canton n’ouvre pas les données d’une autre organisation.
- Recherche inter-organisations : projection minimale et consentie (activité, zone, disponibilité, capacité), sans téléphone ni position exacte publique par défaut.
- Confirmation, plafonds, unicité et journal écrits dans une même transaction ; verrouillage et tests de concurrence réels.
- Les annonces de marché deviennent une projection référencée du chantier canonique. Aucun second compteur ni second état de recrutement indépendant.
- Réutiliser les notifications existantes. Le cron inspecté est quotidien : ne pas promettre une alerte immédiate. Dans le pilote, actualiser à l’ouverture et après action ; définir une cadence compatible avec le budget avant une promesse plus rapide.
- Hors ligne : consultation d’un cache limité et daté, brouillons possibles ; réservation et engagement seulement après confirmation du serveur. Ne pas afficher « confirmé » pendant une synchronisation.
- Suivre montant prévu et heures validées ne signifie pas paiement reçu. Pas de portefeuille réel, séquestre ou versement automatique ouvrier dans le MVP. Les moyens de paiement existants couvrent d’autres usages et nécessitent une conception dédiée.

## 8. Lots d’implantation et critères de sortie

| Lot | Livraison | Critère de sortie |
|---|---|---|
| 0 — Cadrage terrain et données | Cas réels, rôles, règle de surface, taille d’équipe, tarif par personne/équipe, état des bases, décision Supabase/Django | Un scénario accepté de bout en bout et un dictionnaire des données ; compte/carte/mandat identifiés |
| 1 — Moteur métier | Migrations additives, autorisations, équipes, regroupements, transactions et API | Tests d’isolation, seuil, expiration, doublon, retrait et concurrence réussis |
| 2 — Parcours réel léger | Entrées dashboard/Haroo/carte, formulaires courts, recherche et confirmations | Un producteur regroupe et une équipe accepte depuis mobile sans scène 3D ; aucun faux statut signé |
| 3 — Habillage HarooLife | Scène limitée, avatar, trois lieux essentiels, progression issue des API, accès rapide aux actions | Même scénario et mêmes droits en vue simple et interactive ; essais navigateur, clavier et Android réel |
| 4 — Chantier pilote | Planning, heures, contestations, notifications et suivi | Un chantier pilote suivi jusqu’à validation des heures, y compris un refus et une reprise après coupure |
| 5 — Extension | Academy, conseil, météo, préventes/acheteurs selon besoin observé | Chaque connexion apporte une action utile mesurable ; pas de duplication d’identité ou de statut |

Ordre économique : 0 → 1 → 2 → 3 → 4 ; le lot 5 attend les retours du pilote. Ne pas construire une nouvelle ville 3D ni un serveur multijoueur pour valider le recrutement.

## 9. Vérification et mesure

Tests métier : seuil exact, une place restante avec deux demandes simultanées, dernière adhésion après expiration, parcelle déjà engagée, acteur hors organisation, mandat retiré, carte révoquée, double clic/réseau lent, changement des conditions après acceptation, chevauchement des missions, heures contestées. Les tests SQL embarqués ne remplacent pas un test PostgreSQL à plusieurs connexions pour les courses concurrentes.

Parcours E2E : inscription avec intention conservée ; membre par compte ; titulaire par carte ; ouvrier ; administrateur ; accompagnant mandaté. Aucun accès privé par QR seul. Tester également le passage entre compte organisationnel et activité Haroo.

Objectifs proposés à mesurer sur les appareils du pilote : moins de 3 minutes pour publier un besoin avec profil déjà complet ; 30 FPS pour la scène sur le téléphone de référence, sinon proposer la vue légère ; rendu 3D chargé uniquement sur demande ; limiter les requêtes aux ouvertures/actions et suspendre le rafraîchissement en arrière-plan. Mesurer poids transféré, temps de chargement, erreurs et consommation avant de fixer un budget définitif.

Indicateurs produit : délai pour compléter un groupe, taux de propositions acceptées, chantiers effectivement terminés, retraits, litiges et échecs de synchronisation. Les points du jeu et le temps passé ne mesurent pas le travail accompli.

## 10. Mise en service et retour arrière

Utiliser un environnement de test avec données fictives et prestataires désactivés. Appliquer d’abord les migrations additives compatibles, puis les routes sous indicateur d’activation. Activer pour la coopérative pilote après validation. En cas d’incident, couper les nouvelles inscriptions au pilote ou la vue 3D tout en gardant un accès sûr aux engagements existants. Ne pas supprimer les accords ni rouvrir les permissions pour revenir en arrière.

Publication, migration de données réelles et déploiement restent des étapes séparées de ce plan. Aucun calendrier ferme n’est donné avant le lot 0 et l’estimation de chaque lot.

## 11. État de cette étude

- Copie TogoLife préservée ; 14 tests Node exécutés le 10 octobre 2026, tous réussis.
- Ces tests couvrent le prototype solo (simulation, contrôleur, avatar, monde), pas le futur recrutement connecté.
- Aucun test navigateur/Android, intégration Supabase/Django ou engagement réel effectué.
- Seule cette documentation est ajoutée par l’étude ; aucun mécanisme HarooLife réel n’est encore implémenté.
