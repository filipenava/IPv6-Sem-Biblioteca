import tkinter as tk
from tkinter import messagebox, simpledialog

# Classe que representa um endereço IPv6
class IPv6Address:
    def __init__(self, address):
        if isinstance(address, str):
            self.address = self._parse_address(address)
        elif isinstance(address, int):
            self.address = address
        else:
            raise ValueError("Invalid address format")

    def _parse_address(self, address):
        # Divide o endereço em partes separadas por ':'
        parts = address.split(':')
        # Detecta e expande a abreviação '::'
        if '' in parts:
            idx = parts.index('')
            num_missing = 8 - (len(parts) - 1)
            parts = parts[:idx] + ['0'] * num_missing + parts[idx + 1:]
        # Converte cada parte em um inteiro e calcula o endereço completo
        full_address = [int(part, 16) if part else 0 for part in parts]
        return sum(part << (112 - 16 * i) for i, part in enumerate(full_address))

    def __int__(self):
        return self.address

    def __str__(self):
        parts = []
        for i in range(8):
            part = (self.address >> (112 - 16 * i)) & 0xFFFF
            parts.append(f'{part:x}')
        return ':'.join(parts)

    def __eq__(self, other):
        if isinstance(other, IPv6Address):
            return self.address == other.address
        return False

    def __hash__(self):
        return hash(self.address)

    def __lt__(self, other):
        return int(self) < int(other)

# Classe que representa uma rede IPv6
class IPv6Network:
    def __init__(self, base_address):
        self.base_address = IPv6Address(base_address.split('/')[0])
        self.prefix_length = int(base_address.split('/')[1])
        self.start_address = int(self.base_address)
        self.end_address = self.start_address + (1 << (128 - self.prefix_length)) - 1

    # Gera todos os endereços possíveis na rede
    def hosts(self):
        for address in range(self.start_address + 1, self.end_address):
            yield IPv6Address(address)

# Classe que gerencia a alocação de endereços IPv6
class IPv6Manager:
    def __init__(self, base_address):
        self.base_address = IPv6Network(base_address)
        self.allocated_addresses = set()
        self.leftmost_allocations = []
        self.rightmost_allocations = []

    def allocate_leftmost(self):
        """Aloca o endereço IPv6 mais à esquerda disponível."""
        for address in self.base_address.hosts():
            if address not in self.allocated_addresses:
                self.allocated_addresses.add(address)
                self.leftmost_allocations.append(address)
                return address
        return None

    def allocate_rightmost(self):
        """Aloca o endereço IPv6 mais à direita disponível."""
        for address in range(self.base_address.end_address - 1, self.base_address.start_address, -1):
            if IPv6Address(address) not in self.allocated_addresses:
                self.allocated_addresses.add(IPv6Address(address))
                self.rightmost_allocations.append(IPv6Address(address))
                return IPv6Address(address)
        return None

    def release_address(self, address):
        """Libera um endereço IPv6 especificado."""
        if address in self.allocated_addresses:
            self.allocated_addresses.remove(address)
            if address in self.leftmost_allocations:
                self.leftmost_allocations.remove(address)
            elif address in self.rightmost_allocations:
                self.rightmost_allocations.remove(address)

    def get_allocated_addresses(self):
        """Retorna as listas de endereços alocados à esquerda e à direita."""
        return self.leftmost_allocations, self.rightmost_allocations

# Classe que representa a aplicação Tkinter para gerenciar endereços IPv6
class IPv6ManagerApp:
    def __init__(self, root, manager):
        self.manager = manager
        self.root = root
        self.root.title("Gerenciador de IPv6")
        
        # Configura o layout da interface gráfica
        self.setup_gui()

    def setup_gui(self):
        """Configura os elementos da interface gráfica."""
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(padx=10, pady=10)

        self.label = tk.Label(frame, text="Escolha uma ação:")
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

        self.leftmost_button = tk.Button(frame, text="Alocar o endereço mais à esquerda", command=self.allocate_leftmost)
        self.leftmost_button.grid(row=1, column=0, padx=5, pady=5)

        self.rightmost_button = tk.Button(frame, text="Alocar o endereço mais à direita", command=self.allocate_rightmost)
        self.rightmost_button.grid(row=1, column=1, padx=5, pady=5)

        self.release_button = tk.Button(frame, text="Liberar um endereço", command=self.release_address)
        self.release_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.exit_button = tk.Button(frame, text="Sair", command=self.root.quit)
        self.exit_button.grid(row=4, column=0, columnspan=2, pady=5)

        self.leftmost_text = tk.Text(frame, height=10, width=40)
        self.leftmost_text.grid(row=5, column=0, padx=5, pady=5)
        self.leftmost_text.insert(tk.END, "Endereços alocados à esquerda:\n")

        self.rightmost_text = tk.Text(frame, height=10, width=40)
        self.rightmost_text.grid(row=5, column=1, padx=5, pady=5)
        self.rightmost_text.insert(tk.END, "Endereços alocados à direita:\n")

    def allocate_leftmost(self):
        """Manipula a ação de alocar o endereço mais à esquerda."""
        address = self.manager.allocate_leftmost()
        if address:
            messagebox.showinfo("Sucesso", f"Endereço {address} alocado com sucesso.")
        else:
            messagebox.showwarning("Falha", "Nenhum endereço disponível para alocação.")
        self.update_address_lists()

    def allocate_rightmost(self):
        """Manipula a ação de alocar o endereço mais à direita."""
        address = self.manager.allocate_rightmost()
        if address:
            messagebox.showinfo("Sucesso", f"Endereço {address} alocado com sucesso.")
        else:
            messagebox.showwarning("Falha", "Nenhum endereço disponível para alocação.")
        self.update_address_lists()

    def release_address(self):
        """Manipula a ação de liberar um endereço."""
        address_to_release = simpledialog.askstring("Liberar endereço", "Digite o endereço IPv6 a ser liberado:")
        if address_to_release:
            try:
                address = IPv6Address(address_to_release)
                self.manager.release_address(address)
                messagebox.showinfo("Sucesso", f"Endereço {address} liberado com sucesso.")
            except ValueError:
                messagebox.showerror("Erro", "Endereço IPv6 inválido.")
        self.update_address_lists()

    def show_allocated_addresses(self):
        """Manipula a ação de mostrar endereços alocados."""
        self.update_address_lists()

    def update_address_lists(self):
        """Atualiza as listas de endereços alocados na interface."""
        leftmost_addresses, rightmost_addresses = self.manager.get_allocated_addresses()
        self.leftmost_text.delete(1.0, tk.END)
        self.rightmost_text.delete(1.0, tk.END)
        self.leftmost_text.insert(tk.END, "Endereços alocados à esquerda:\n")
        self.rightmost_text.insert(tk.END, "Endereços alocados à direita:\n")
        for addr in leftmost_addresses:
            self.leftmost_text.insert(tk.END, f"{addr}\n")
        for addr in rightmost_addresses:
            self.rightmost_text.insert(tk.END, f"{addr}\n")

def main():
    base_address = "2001:db8::/32"
    manager = IPv6Manager(base_address)

    root = tk.Tk()
    app = IPv6ManagerApp(root, manager)
    root.mainloop()

if __name__ == "__main__":
    main()
