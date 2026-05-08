# Guide de Préparation : Soutenance Projet SecurAccess

Ce document est conçu pour vous aider à comprendre, maîtriser et défendre votre projet (SecurAccess) devant votre professeur, même si vous n'avez pas codé chaque ligne.

> [!NOTE]
> L'objectif n'est pas d'apprendre le code par cœur, mais de comprendre **l'architecture globale**, les **choix technologiques** et les **limites du système**.

---

## 1. Résumé Haut Niveau (En termes simples)

**"Que fait ce projet ?"**
SecurAccess est une application de contrôle d'accès sécurisé qui combine deux domaines technologiques : la **biométrie** et le **tatouage numérique** (cryptographie).

1.  **La Biométrie (Reconnaissance Faciale) :** Au lieu d'utiliser un mot de passe ou un badge, l'application utilise la webcam pour détecter le visage d'une personne, le transformer en une signature mathématique unique (grâce à l'intelligence artificielle), et vérifier si cette personne a le droit d'entrer.
2.  **Le Tatouage Numérique des Logs :** À chaque fois que quelqu'un essaie de se connecter, l'application enregistre cette tentative dans une base de données. Pour s'assurer qu'aucun pirate (ou administrateur malveillant) ne modifie ou n'efface ces historiques pour couvrir ses traces, chaque ligne d'historique est "tatouée" avec une signature cryptographique indétectable et infalsifiable.

---

## 2. Terminologie et Concepts Clés (À connaître absolument)

Pour paraître compétent, vous devez utiliser les bons mots. Voici les concepts centraux :

*   **Haar Cascade (OpenCV) :** C'est l'algorithme "classique" utilisé pour *trouver* le visage dans l'image. Il ne reconnaît pas *qui* est la personne, il dit juste "voici un visage".
*   **ArcFace (InsightFace) :** C'est le modèle d'Intelligence Artificielle (Deep Learning) utilisé pour la *reconnaissance*. Il prend le visage détecté et le convertit en un vecteur mathématique.
*   **Embedding (Vecteur de caractéristiques) :** C'est une liste de 512 nombres générée par ArcFace. C'est la "signature" ou l'"empreinte digitale" mathématique du visage.
*   **Distance Euclidienne :** C'est la méthode de calcul utilisée pour comparer deux visages. Le système calcule la distance mathématique entre l'embedding capturé par la webcam et l'embedding sauvegardé dans la base de données. Plus la distance est proche de zéro, plus les visages se ressemblent. (Le seuil strict du projet est fixé à 0.75).
*   **HMAC-SHA256 :** C'est l'algorithme cryptographique utilisé pour le "tatouage" (watermarking) des logs. Il prend les données du log et une clé secrète, et génère une signature unique. Si un seul caractère du log est modifié, la signature devient invalide.
*   **Spoofing :** Une attaque où quelqu'un essaie de tromper le système, par exemple en montrant une photo imprimée ou une vidéo de quelqu'un d'autre à la caméra.

---

## 3. Questions Probables du Professeur & Modèles de Réponses

> [!IMPORTANT]
> Les professeurs aiment tester si vous comprenez *pourquoi* vous avez fait un choix, plutôt que *comment* vous l'avez codé.

**Q1 : Pourquoi utiliser ArcFace plutôt qu'un algorithme plus ancien comme EigenFaces ou FisherFaces ?**
**Réponse :** "ArcFace est un modèle de Deep Learning de l'état de l'art. Contrairement aux anciennes méthodes qui sont très sensibles aux variations de lumière ou d'expression faciale, ArcFace projette les visages dans un espace mathématique où les visages de la même personne sont regroupés très proches les uns des autres (grâce à sa fonction de perte 'Additive Angular Margin'). C'est beaucoup plus robuste et précis."

**Q2 : Le projet parle de 'Tatouage Numérique'. Expliquez-moi comment vous l'avez appliqué. Il ne s'agit pas de cacher une image dans une image ?**
**Réponse :** "Exactement, nous n'avons pas fait de tatouage d'image (*watermarking* visuel). Nous avons appliqué le concept du tatouage à la sécurité des données d'historique (les logs). Nous utilisons un algorithme de hachage (HMAC-SHA256) avec une clé secrète pour signer chaque log dans la base de données SQLite. Cela garantit l'intégrité de notre audit d'accès : si quelqu'un modifie la base de données en dehors de l'application, le système le détectera car la signature ne correspondra plus."

**Q3 : Comment choisissez-vous le seuil d'acceptation (le fameux 0.75) ?**
**Réponse :** "C'est un compromis entre le FAR (False Acceptance Rate - laisser entrer un intrus) et le FRR (False Rejection Rate - bloquer une personne légitime). Nous avons choisi un seuil strict de 0.75 pour la distance euclidienne afin de privilégier la sécurité (minimiser le FAR), quite à demander à l'utilisateur de se replacer s'il est mal détecté."

**Q4 : Que se passe-t-il si la lumière est très mauvaise ?**
**Réponse :** "Le système possède une première étape de détection (Haar Cascade) avec une égalisation d'histogramme pour améliorer le contraste. Cependant, si la lumière est vraiment trop faible, le détecteur Haar Cascade risque de ne pas trouver le visage du tout, ou ArcFace pourrait générer un embedding faussé."

---

## 4. Faiblesses et Limites du Projet (À anticiper)

Les professeurs chercheront la petite bête. C'est une excellente chose d'**admettre les limites de son propre projet avant même qu'on vous le reproche**. Cela montre votre maturité technique.

> [!WARNING]
> Préparez-vous à mentionner ces points si on vous demande "Que feriez-vous pour améliorer le système si vous aviez 3 mois de plus ?"

*   **Absence de "Liveness Detection" (Détection de Vivacité) :** C'est la plus grande faille. Actuellement, si quelqu'un montre une vidéo haute définition sur un grand écran (Replay Attack), le système risque de l'accepter, car la distance euclidienne s'approche de la zone de validité.
    *   *La parade verbale :* "Nous avons testé la résistance au spoofing par photo imprimée (qui échoue), mais nous avons constaté qu'une vidéo HD est dangereuse. L'amélioration principale serait d'ajouter un module d'analyse de texture ou de détection de clignement d'yeux pour s'assurer que l'utilisateur est vivant."
*   **Détection Haar Cascade un peu ancienne :** Haar Cascade est rapide mais il est sensible aux rotations du visage.
    *   *La parade verbale :* "Nous l'avons choisi pour sa légèreté afin de garantir une interface fluide, mais pour une V2, nous passerions à MTCNN ou RetinaFace qui sont plus robustes aux visages de profil."
*   **Base de données locale (SQLite) :** Le système n'est pas "distribué".
    *   *La parade verbale :* "Pour une vraie entreprise avec plusieurs portes d'accès, il faudrait migrer SQLite vers PostgreSQL avec une API REST centralisée."

---

## 5. Comment expliquer votre propre contribution (Exemples)

Même si votre contribution technique a été mineure, vous devez la présenter sous l'angle de la **valeur ajoutée**. Voici quelques façons de tourner les choses selon ce que vous avez fait :

**Si vous avez fait de l'interface (UI) / Intégration :**
> "Je me suis concentré sur l'architecture de l'interface graphique (PyQt5) et l'intégration des différents services. Un algorithme puissant ne sert à rien si les agents de sécurité ne peuvent pas l'utiliser. J'ai veillé à ce que les retours du service de reconnaissance (comme 'Visage inconnu') soient traduits en états d'interface clairs et sans latence bloquante pour l'utilisateur."

**Si vous avez fait des tests et de la collecte de données :**
> "Mon rôle principal a été la validation et l'assurance qualité. J'ai conçu les protocoles de tests de 'spoofing' (photos, écrans) pour stress-tester nos modèles. C'est grâce à cette phase que nous avons pu calibrer précisément notre seuil de distance euclidienne à 0.75, en observant concrètement à quel moment le système commençait à confondre un vrai visage avec une photo."

**Si vous avez fait la conception de la base de données et des logs :**
> "Je me suis occupé de l'infrastructure de données et de la sécurité de l'audit. J'ai structuré la base SQLite et, surtout, j'ai implémenté la logique du 'tatouage' cryptographique (HMAC). J'ai veillé à ce que la séparation des rôles (Admin vs User) soit respectée et que chaque tentative d'accès laisse une trace infalsifiable."

**Si vous avez écrit une grande partie du rapport :**
> "J'ai pris en charge la synthèse architecturale et la documentation technique. J'ai analysé le code de mes camarades pour le formaliser (diagrammes de classes, flux d'authentification). Cela m'a permis d'avoir une vision globale du projet, depuis la capture OpenCV jusqu'au stockage sécurisé, pour garantir que notre réalisation correspondait parfaitement au cahier des charges initial."
