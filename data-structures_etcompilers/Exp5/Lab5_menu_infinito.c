// === Playlist Infinita con Tabla de Dispersión ===
// Lenguaje: C (para terminal en Linux/WSL)
// Este programa simula un menú infinito que representa una lista circular
// Al seleccionar una opción (con Enter), muestra un mensaje relacionado almacenado en una tabla hash
// Tema didáctico: circularidad, estructura de datos, eficiencia en búsqueda, analogía con compiladores y flujos de datos

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>

// ==============================
// Sección: Entrada sin Enter
// ==============================
// Esta función permite capturar teclas sin necesidad de presionar Enter
char getch() {
    struct termios oldt, newt;
    char ch;
    tcgetattr(STDIN_FILENO, &oldt);           // Guardamos la configuración actual de la terminal
    newt = oldt;
    newt.c_lflag &= ~(ICANON | ECHO);         // Desactivamos el modo canónico y eco
    tcsetattr(STDIN_FILENO, TCSANOW, &newt);  // Aplicamos la nueva configuración
    ch = getchar();                           // Leemos un carácter
    tcsetattr(STDIN_FILENO, TCSANOW, &oldt);  // Restauramos configuración original
    return ch;
}

// ======================
// Sección: Tabla Hash
// ======================
#define TABLE_SIZE 10

// Estructura para nodo de la lista enlazada
struct Node {
    char *key;            // Identificador, e.g., "fase_1"
    char *value;          // Descripción asociada
    struct Node *next;    // Apunta al siguiente nodo (encadenamiento)
};

// Tabla de dispersión (array de punteros a Node)
struct Node* hashTable[TABLE_SIZE];

// Función hash simple: suma de caracteres mod TABLE_SIZE
int hash(char *key) {
    int sum = 0;
    for (int i = 0; key[i] != '\0'; i++) {
        sum += key[i];
    }
    return sum % TABLE_SIZE;
}

// Insertar par clave/valor en tabla hash
void insert(char *key, char *value) {
    int index = hash(key);                             // Calculamos índice hash
    struct Node *newNode = malloc(sizeof(struct Node));
    newNode->key = key;
    newNode->value = value;
    newNode->next = hashTable[index];                 // Encadenamiento (inserta al inicio)
    hashTable[index] = newNode;
}

// Buscar una clave en la tabla hash
char* search(char *key) {
    int index = hash(key);
    struct Node *current = hashTable[index];
    while (current) {
        if (strcmp(current->key, key) == 0)
            return current->value;                   // Si la clave coincide, devuelve el valor
        current = current->next;
    }
    return "[Información no encontrada]";
}

// ======================
// Sección: Menú Circular
// ======================
#define NUM_OPTIONS 5
char *options[NUM_OPTIONS] = {
    "fase_1",
    "fase_2",
    "fase_3",
    "fase_4",
    "fase_5"
};

int main() {
    // Insertamos los datos del "plan de vuelo" en la tabla hash
    insert("fase_1", "Encendido de motores y chequeo inicial");
    insert("fase_2", "Ascenso vertical y control de trayectoria");
    insert("fase_3", "Separación de etapas y estabilización");
    insert("fase_4", "Ingreso a órbita y ajustes de velocidad");
    insert("fase_5", "Liberación de carga útil y fin de misión");

    int selected = 0;
    char c;

    while (1) {
        printf("\033[H\033[J"); // Limpia la pantalla
        printf("=== MENU DE FASES DEL COHETE ===\n\n");

        // Mostramos las opciones con la flecha -> en la opción actual
        for (int i = 0; i < NUM_OPTIONS; i++) {
            if (i == selected)
                printf("-> %s\n", options[i]);
            else
                printf("   %s\n", options[i]);
        }

        printf("\nUse 'w' y 's' para moverse. Presione ENTER para seleccionar.\n");
        c = getch();

        // Movimiento circular hacia arriba
        if (c == 'w') {
            selected = (selected - 1 + NUM_OPTIONS) % NUM_OPTIONS;
        }
        // Movimiento circular hacia abajo
        else if (c == 's') {
            selected = (selected + 1) % NUM_OPTIONS;
        }
        // Selecciona la opción y muestra su descripción
        else if (c == '\n') {
            printf("\n>> %s: %s\n", options[selected], search(options[selected]));
            printf("Presione cualquier tecla para continuar...\n");
            getch();
        }
    }

    return 0;
}
