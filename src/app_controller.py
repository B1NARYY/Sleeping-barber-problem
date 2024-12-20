# src/app_controller.py

import threading
from src.models import URLQueue, Parser, PageFetcher, Crawler, URLProducer, normalize_url
from src.config import Config
from src.utils import user_print


"""
AppController manages the main flow of the Barber Simulation:
- Handles configuration, URL queue, and thread management.
- Controls the lifecycle of the simulation (start, stop, reset).
- Provides utilities for managing customers and links.
"""


class AppController:
    """
    Main controller for managing the simulation.
    """
    def __init__(self, config_path):
        """
        Initializes the AppController.

        Args:
            config_path (str): Path to the configuration file.
        """
        self.config_path = config_path
        self.reset()

    def reset(self):
        """
        Resets the application by reloading the configuration
        and reinitializing all components.
        """
        self.config = Config()
        self.config.load(self.config_path)
        self.url_queue = URLQueue()
        self.parser = Parser()
        self.fetcher = PageFetcher(max_retries=3)
        self.visited = set()
        self.lock = threading.Lock()
        self.crawler = None
        self.producer_thread = None
        self.running = False
        self.customers_info = []
        self.stored_links = []

    def add_customer(self, customer):
        """
        Adds a processed customer to the list.

        Args:
            customer (Customer): Processed customer data.
        """
        with self.lock:
            self.customers_info.append(customer)

    def is_running(self):
        """
        Checks if the simulation is currently running.

        Returns:
            bool: True if running, False otherwise.
        """
        return self.running

    def start(self):
        """
        Starts the simulation by initializing and starting
        the Crawler and URLProducer threads.
        """
        if self.running:
            user_print("Barber is already running.")
            return
        self.running = True

        # Add initial URLs to the queue
        initial_urls = self.config.get('initial_urls', [])
        for u in initial_urls:
            normalized_url = normalize_url(u)
            if normalized_url not in self.visited:
                self.url_queue.put_url(normalized_url)
                self.visited.add(normalized_url)

        # Start Crawler thread
        self.crawler = Crawler(
            url_queue=self.url_queue,
            parser=self.parser,
            fetcher=self.fetcher,
            visited=self.visited,
            lock=self.lock,
            config=self.config,
            keywords=self.keywords,
            app_controller=self
        )
        self.crawler.start()

        # Start URLProducer thread
        self.producer_thread = URLProducer(self.url_queue, self.config, None)
        self.producer_thread.set_app_controller(self)
        self.producer_thread.start()

    def stop(self):
        """
        Stops the simulation and ensures all threads are properly terminated.
        """
        if not self.running:
            return
        self.running = False

        # Signal the Crawler thread to stop
        self.url_queue.put_url(None)
        if self.crawler is not None:
            self.crawler.join()

        # Stop the Producer thread
        if self.producer_thread is not None:
            self.producer_thread.running = False
            self.producer_thread.join()

        self.crawler = None
        self.producer_thread = None

    def show_customers(self):
        """
        Displays all processed customers.
        """
        with self.lock:
            if not self.customers_info:
                user_print("No customers processed.")
            else:
                user_print("Processed customers:")
                for c in self.customers_info:
                    user_print(str(c))
                user_print("This is end of the simulation.")

    @property
    def keywords(self):
        """
        Retrieves the list of keywords from the configuration.

        Returns:
            list: List of keywords.
        """
        return self.config.get('keywords', [])

    def status(self):
        """
        Returns the current status of the simulation.

        Returns:
            str: Status message indicating if the simulation is running or stopped.
        """
        if self.running:
            return "Simulation is running."
        else:
            return "Simulation is not running."

    def store_links(self, links):
        """
        Stores a list of links for future processing.

        Args:
            links (list): List of links to store.
        """
        with self.lock:
            for link in links:
                if link not in self.visited and link not in self.stored_links:
                    self.stored_links.append(link)

    def pop_stored_link(self):
        """
        Retrieves and removes a stored link for processing.

        Returns:
            str or None: The next stored link, or None if none exist.
        """
        with self.lock:
            if self.stored_links:
                return self.stored_links.pop(0)
            return None

    def reload_config(self):
        """
        Reloads the configuration to apply any changes made to the config file.
        """
        self.config.reload()
