import spotipy
import spotipy.util as util
import random
import os

# Função para limpar terminal
def limpartela():
    if os.name == 'posix':  # Verifica se o sistema operacional é Unix/Linux/Mac
        os.system('clear')
    elif os.name == 'nt':  # Verifica se o sistema operacional é Windows
        os.system('cls')
        
# Configurações de autenticação (substitua com suas próprias credenciais)
username = 'SeuNomeDeUsuario'
scope = 'playlist-modify-public'
client_id = 'SeuClientID'
client_secret = 'SeuClientSecret'
redirect_uri = 'http://localhost:8080/callback'

# Função para ler inteiros
def leiaInt(msg):
    valor = 0
    while True:
        n = input(msg).strip()
        try:
            valor = int(n)
        except (TypeError, ValueError):
            print('ERRO! Digite uma opção válida.')
        else:
            break
    return valor 

# Função para limpar uma playlist
def limpar_playlist(sp, username, playlist_id):
    # Obtém todas as faixas da playlist
    tracks = sp.user_playlist_tracks(username, playlist_id)['items']

    if len(tracks) == 0:
        print("A playlist já está vazia.")
        return

    # Remove cada faixa da playlist
    for track in tracks:
        track_id = track['track']['id']
        sp.user_playlist_remove_all_occurrences_of_tracks(username, playlist_id, [track_id])

    print("Playlist limpa com sucesso!")

# Função para reordenar uma playlist aleatoriamente
def reordenar_playlist_aleatoriamente(sp, username, playlist_id):
    # Obtenha as faixas da playlist atual
    playlist = sp.user_playlist_tracks(user=username, playlist_id=playlist_id)

    # Extraia as IDs das faixas
    track_ids = set()
    track_ids = [track['track']['id'] for track in playlist['items']]
    
    if len(track_ids) == 0:
        print("A playlist está vazia.")
        return

    # Embaralhar as faixas aleatoriamente
    random.shuffle(track_ids)
    
    # Remova todas as faixas da playlist
    sp.user_playlist_remove_all_occurrences_of_tracks(user=username, playlist_id=playlist_id, tracks=track_ids)

    # Reordenar a playlist com base na nova ordem
    try:
        sp.user_playlist_add_tracks(user=username, playlist_id=playlist_id, tracks=track_ids)
        print("Playlist reordenada aleatoriamente com sucesso!")
    except Exception as e:
        print("Erro ao reordenar a playlist:", e)

# Função para autenticar e obter um token de acesso
def autenticar_spotify():
    token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
    if token:
        return spotipy.Spotify(auth=token)
    else:
        print("Não foi possível obter o token.")
        return None

# Função para criar uma nova playlist
def criar_playlist(sp, playlist_name, public=True, description=''):
    playlist = sp.user_playlist_create(user=username, name=playlist_name, public=public, description=description)
    return playlist

# Função para buscar e adicionar faixas de artistas à playlist
def adicionar_faixas_a_playlist(sp, username, playlist_id, artistas):
    tracks = []
    limite = leiaInt('Quantas músicas por artista: ')
    for artista in artistas:
        result = sp.search(artista, limit=limite, type='track')
        for track in result['tracks']['items']:
            tracks.append(track['id'])
            print("Adicionando a faixa:", track['name'], "-", track['artists'][0]['name'])
    random.shuffle(tracks)
    while tracks:
        try:
            result = sp.user_playlist_add_tracks(username, playlist_id, tracks[:50])
        except Exception as e:
            print("Erro ao adicionar faixas à playlist:", e)
        tracks = tracks[50:]
    print("Faixas adicionadas à playlist com sucesso!")

# Função para listar as playlists do usuário
def listar_playlists(sp):
    playlists = sp.user_playlists(user=username)
    if playlists:
        print("Suas playlists:")
        for i, playlist in enumerate(playlists['items']):
            print(f"{i + 1}. {playlist['name']}")
        return playlists['items']
    else:
        print("Você não tem playlists.")
        return []

# Função que adiciona os artistas na lista
def adicionar_artistas():
    artistas = []
    while True:
        artista = input('Digite o nome do artista (ou deixe em branco para sair): ')
        if not artista:
            break
        artistas.append(artista)
    return artistas

# Função que adicionar por estilo musical
def adicionar_genero(sp, username, playlist_id, playlist_name):
    # Gênero que você deseja pesquisar
    genero = input('Digite o estilo musical: ').lower()  # Substitua com o gênero desejado
    # País em que deseja realizar a pesquisa
    pais = input('Digite a sigla do país que quer fazer a busca (ex: US): ').upper()  # Substitua com o código do país desejado
    limite = leiaInt('Digite o total de músicas que deseja adicionar na Playist: ')
    tracks = []
    offset = 0
    # Pesquise playlists relacionadas ao gênero
    try:
        while offset < limite:
            resultados = sp.search(q=f'genre:{genero}', type='track', market=pais, limit=50, offset=offset)
            # Imprima as faixas encontradas
            for track in resultados['tracks']['items']:
                tracks.append(track['id'])
                print("Adicionando a faixa:", track['name'], "-", track['artists'][0]['name'])
            offset += 50

        random.shuffle(tracks)

        # Adiciona as faixas à playlist criada anteriormente
        while tracks:
            try:
                sp.user_playlist_add_tracks(user=username, playlist_id=playlist_id, tracks=tracks[0:50])
            except Exception as e:
                print("Erro ao adicionar faixas à playlist:", e)
            tracks = tracks[50:]
        print(f'Músicas em alta do gênero "{genero}" adicionadas à playlist "{playlist_name}"!')  
    except Exception as e:
        print("Erro ao pesquisar faixas:", e)
            
# Função principal
def main():
    sp = autenticar_spotify()
    if not sp:
        return

    print("Bem-vindo ao Spotify Playlist Generator!")

    while True:
        print("\nMenu Principal:")
        print("1. Criar uma Nova Playlist")
        print("2. Adicionar Faixas de Artistas à Playlist")
        print("3. Adicionar Faixas por gênero à Playlist")
        print("4. Limpar/Reorganizar Playlist.")
        print("5. Sair")

        escolha = leiaInt("Escolha uma opção: ")

        match escolha:
            case 1:
                limpartela()
                playlist_name = input("Digite o nome da playlist: ")
                public = input("A playlist será pública? (S/N): ").lower() == 's'
                description = input("Digite uma descrição para a playlist: ")
                criar_playlist(sp, playlist_name, public, description)
                print(f"Playlist '{playlist_name}' criada com sucesso!")

            case 2:
                limpartela()
                playlists = listar_playlists(sp)
                if playlists:
                    escolha_playlist = input("Escolha o número da playlist para adicionar faixas: ")
                    if escolha_playlist.isdigit() and 1 <= int(escolha_playlist) <= len(playlists):
                        playlist_id = playlists[int(escolha_playlist) - 1]['id']
                        artistas = adicionar_artistas()
                        adicionar_faixas_a_playlist(sp, username, playlist_id, artistas)
                    else:
                        print("Escolha inválida. Tente novamente.")
                else:
                    print('Você não tem playlists!')

            case 3:
                limpartela()
                playlists = listar_playlists(sp)
                if playlists:
                    escolha_playlist = input("Escolha o número da playlist para adicionar faixas: ")
                    if escolha_playlist.isdigit() and 1 <= int(escolha_playlist) <= len(playlists):
                        playlist_id = playlists[int(escolha_playlist) - 1]['id']
                        playlist_name = playlists[int(escolha_playlist) - 1]['name']
                        adicionar_genero(sp, username, playlist_id, playlist_name)
                    else:
                        print("Escolha inválida. Tente novamente.")               
                else:
                    print('Você não tem playlists!')
            
            case 4:
                limpartela()
                playlists = listar_playlists(sp)
                if playlists:
                    escolha_playlist = input("Escolha o número da playlist: ")
                    if escolha_playlist.isdigit() and 1 <= int(escolha_playlist) <= len(playlists):
                        playlist_id = playlists[int(escolha_playlist) - 1]['id']
                        playlist_name = playlists[int(escolha_playlist) - 1]['name']
                        print("1. Limpar Playlist\n2. Reorganizar Playlist.")
                        op = leiaInt(': ')
                        match op:
                            case 1:
                                limpar_playlist(sp, username, playlist_id)
                            case 2:
                                reordenar_playlist_aleatoriamente(sp, username, playlist_id)
                            case _:
                                print('Opção invalida!')
                    else:
                        print("Escolha inválida. Tente novamente.")               
                else:
                    print('Você não tem playlists!')               
            
            case 5:
                print("Saindo do programa.")
                break

            case _:
                print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    limpartela()
    main()
