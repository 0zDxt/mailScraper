#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
import time
import argparse
import csv
import random
from urllib.parse import urljoin, urlparse
import sys

# --- Configuration ------------

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
]
HEADERS = {'User-Agent': random.choice(USER_AGENTS)}
TIMEOUT = 10
DELAY = (1.5, 3.5)
MAX_PAGES = 3
MAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')


# --- Recherche DuckDuckGo --------------

def search_duckduckgo(query, num_pages=1):
    urls = []
    session = requests.Session()
    for page in range(num_pages):
        url = "https://html.duckduckgo.com/html/"
        data = {'q': query, 's': page * 30}
        try:
            response = session.post(url, data=data, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for a in soup.find_all('a', class_='result__a', href=True):
                href = a['href']
                if 'uddg=' in href:
                    clean = requests.utils.unquote(href.split('uddg=')[1].split('&')[0])
                elif href.startswith('http'):
                    clean = href
                else:
                    continue
                if clean not in urls:
                    urls.append(clean)
            print(f"  Page {page + 1} → {len([u for u in urls if u not in urls[:page*30]])} nouveaux liens")
            time.sleep(random.uniform(*DELAY))
        except Exception as e:
            print(f"  Erreur page {page + 1} : {e}")
    return urls


# --- Filtre intelligent par activité -----------

def is_relevant_website(url, activite):
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path.lower()

    # --- Exclusions universelles --------------
    exclude_domains = [
        'facebook.com', 'instagram.com', 'twitter.com', 'linkedin.com',
        'youtube.com', 'wikipedia.org', 'duckduckgo.com', 'google.com', 'cnil.fr', 'pariszigzag.fr',
        'citycrunch.fr'
    ]
    if any(ex in domain for ex in exclude_domains):
        return False

    # --- Exclusions par activité --------------
    exclude_by_activite = {
        'restaurant': ['tripadvisor.', 'lafourchette.', 'yelp.'],
        'coiffeur': ['treatwell.', 'plancity.'],
        'garagiste': ['idgarages.', 'vroomly.'],
        'avocat': ['avocat.fr', 'juritravail.'],
    }
    if activite in exclude_by_activite:
        if any(ex in domain for ex in exclude_by_activite[activite]):
            return False

    # --- Mots-clés positifs ------------------
    keywords = {
        'immobilière': ['immobilier', 'agence', 'immo'],
        'restaurant': ['restaurant', 'resto', 'bistro', 'brasserie', 'cuisine'],
        'coiffeur': ['coiffure', 'salon', 'coiffeur', 'barber'],
        'garagiste': ['garage', 'mecanique', 'reparation', 'auto'],
        'avocat': ['avocat', 'cabinet', 'juridique', 'droit'],
    }

    act_key = next((k for k in keywords if k in activite), 'autre')
    relevant = any(k in domain + path for k in keywords.get(act_key, [activite.lower()]))

    return relevant


# --- Extraction e-mails ---

def extract_emails_from_url(url, visited=None):
    if visited is None:
        visited = set()
    if url in visited:
        return set()
    visited.add(url)
    emails = set()

    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if response.status_code != 200:
            return set()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        # Regex
        emails.update(MAIL_REGEX.findall(text))

        # mailto:
        for a in soup.find_all('a', href=True):
            if 'mailto:' in a['href']:
                email = a['href'].split('mailto:')[1].split('?')[0].strip()
                if email:
                    emails.add(email)

        # Suivre page contact
        contact_texts = ['contact', 'nous contacter', 'contactez-nous', 'mention', 'rgpd', 'legal']
        for a in soup.find_all('a', href=True):
            link_text = a.get_text(strip=True).lower()
            if any(k in link_text for k in contact_texts):
                link = urljoin(url, a['href'])
                if link != url and link not in visited and 'pdf' not in link.lower():
                    print(f"    → Suivi : {link}")
                    emails.update(extract_emails_from_url(link, visited))
                    time.sleep(random.uniform(*DELAY))

        return {e for e in emails if e}

    except Exception as e:
        print(f"    Erreur : {e}")
        return set()


# --- Main ----------------

def main():
    parser = argparse.ArgumentParser(
        description="Scraper éthique d'e-mails professionnels (toutes activités)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("ville", help="Ville cible (ex: Lyon, Paris)")
    parser.add_argument("--activite", "-a", required=True, help="Activité (ex: coiffeur, restaurant, avocat)")
    parser.add_argument("--pages", "-p", type=int, default=MAX_PAGES, help="Pages à parcourir")
    parser.add_argument("--output", "-o", default="pros_emails.csv", help="Fichier CSV de sortie")
    args = parser.parse_args()

    ville = args.ville.strip().title()
    activite = args.activite
    query = f"{activite} {ville} site:.fr"

    print(f"""
SCRAPER PRO ÉTHIQUE
Ville : {ville}
Activité : {activite}
Recherche : "{query}"
Pages : {args.pages}
Sortie : {args.output}
""")
    print("=" * 70)

    # 1. Recherche
    print("Étape 1 : Recherche DuckDuckGo...")
    candidate_urls = search_duckduckgo(query, num_pages=args.pages)

    # 2. Filtre
    print(f"\nÉtape 2 : Filtrage des sites pertinents...")
    relevant_urls = [u for u in candidate_urls if is_relevant_website(u, activite)]
    print(f"{len(relevant_urls)} sites pertinents trouvés")

    # 3. Extraction
    print(f"\nÉtape 3 : Extraction des e-mails...")
    results = {}
    for i, url in enumerate(relevant_urls, 1):
        print(f"[{i}/{len(relevant_urls)}] {url}")
        emails = extract_emails_from_url(url)
        if emails:
            results[url] = list(emails)
            print(f"    E-mails : {', '.join(emails)}")
        else:
            print("    Aucun e-mail")
        time.sleep(random.uniform(*DELAY))

    # 4. CSV
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Ville', 'Activité', 'URL', 'Email'])
        for url, emails in results.items():
            for email in emails:
                writer.writerow([ville, activite.title(), url, email])

    print("=" * 70)
    print(f"TERMINE ! {len(results)} pros avec e-mail trouvés.")
    print(f"Résultats → {args.output}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nArrêt utilisateur.")
        sys.exit(0)
