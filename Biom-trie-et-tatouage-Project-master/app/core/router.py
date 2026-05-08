# =============================================================================
# core/router.py
# Gestionnaire de navigation entre les pages de l'application
#
# Le Router utilise un QStackedWidget pour gérer les pages comme un "deck".
# Le principe : chaque page est empilée, on affiche uniquement la page courante.
# L'avantage : pas de fermeture/ouverture de fenêtres, navigation fluide.
# =============================================================================

from PyQt5.QtWidgets import QStackedWidget, QMainWindow


class Router:
    """
    Gère la navigation entre les différentes pages de l'application.

    Principe de fonctionnement :
    - Chaque page (LoginPage, WelcomePage, etc.) est ajoutée au QStackedWidget.
    - La navigation se fait via router.navigate("login"), router.navigate("welcome"), etc.
    - Les pages sont créées une seule fois et réutilisées.

    Usage dans une page :
        from app.core.router import Router
        Router.get_instance().navigate("welcome")
    """

    _instance: "Router" = None  # Singleton

    def __init__(self):
        self._stack: QStackedWidget = None      # Widget contenant les pages
        self._pages: dict = {}                  # Dictionnaire nom_page -> index
        self._history: list = []                # Historique pour "retour arrière"

    @classmethod
    def get_instance(cls) -> "Router":
        """Retourne l'instance unique du Router."""
        if cls._instance is None:
            cls._instance = Router()
        return cls._instance

    def initialize(self, stack: QStackedWidget) -> None:
        """
        Initialise le router avec le QStackedWidget de la fenêtre principale.
        Doit être appelé une seule fois au démarrage de l'application.
        """
        self._stack = stack

    def register_page(self, name: str, widget) -> None:
        """
        Enregistre une page dans le router.

        Args:
            name   : Identifiant unique de la page (ex: "login", "welcome").
            widget : Instance du widget de la page.
        """
        if self._stack is None:
            raise RuntimeError("Router non initialisé. Appelez initialize() d'abord.")

        index = self._stack.addWidget(widget)
        self._pages[name] = index

    def navigate(self, page_name: str) -> None:
        """
        Navigue vers la page dont le nom est donné.
        Ajoute la page courante à l'historique de navigation.

        Args:
            page_name : Nom de la page cible (ex: "login", "admin_dashboard").
        """
        if page_name not in self._pages:
            raise ValueError(f"Page inconnue : '{page_name}'. Pages disponibles : {list(self._pages.keys())}")

        # Sauvegarder la page courante dans l'historique
        current_index = self._stack.currentIndex()
        current_name  = self._get_name_by_index(current_index)
        if current_name and current_name != page_name:
            self._history.append(current_name)

        # Afficher la nouvelle page
        self._stack.setCurrentIndex(self._pages[page_name])

    def go_back(self) -> bool:
        """
        Revient à la page précédente dans l'historique.

        Returns:
            bool : True si le retour a été effectué, False si historique vide.
        """
        if not self._history:
            return False

        previous_page = self._history.pop()
        self._stack.setCurrentIndex(self._pages[previous_page])
        return True

    def clear_history(self) -> None:
        """Vide l'historique de navigation (utile lors du logout)."""
        self._history.clear()

    def get_current_page_name(self) -> str:
        """Retourne le nom de la page actuellement affichée."""
        current_index = self._stack.currentIndex()
        return self._get_name_by_index(current_index)

    def get_page(self, name: str):
        """Retourne l'instance de page enregistree, ou None."""
        if name not in self._pages:
            return None
        return self._stack.widget(self._pages[name])

    def _get_name_by_index(self, index: int) -> str:
        """Recherche inverse : index -> nom de page."""
        for name, idx in self._pages.items():
            if idx == index:
                return name
        return ""
