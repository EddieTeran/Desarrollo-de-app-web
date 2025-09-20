/**
 * Script principal para Caprichos Store
 * Funcionalidades: Galería interactiva, formulario de suscripción, catálogo dinámico
 */

// ===== CONFIGURACIÓN GLOBAL =====
const CONFIG = {
    gallery: {
        maxImages: 12,
        defaultImageSize: '200px'
    },
    validation: {
        minPasswordLength: 6,
        minNameLength: 3,
        minAge: 18
    }
};

// ===== GALERÍA INTERACTIVA =====
class GalleryManager {
    constructor() {
        this.gallery = document.getElementById('gallery');
        this.addBtn = document.getElementById('addImageBtn');
        this.removeBtn = document.getElementById('removeImageBtn');
        this.urlInput = document.getElementById('imageUrl');
        this.selectedImage = null;
        
        this.init();
    }

    init() {
        if (this.addBtn) {
            this.addBtn.addEventListener('click', () => this.addImage());
        }
        if (this.removeBtn) {
            this.removeBtn.addEventListener('click', () => this.removeSelectedImage());
        }
        if (this.urlInput) {
            this.urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.addImage();
                }
            });
        }
    }

    addImage() {
        const imageUrl = this.urlInput.value.trim();
        
        if (!imageUrl) {
            this.showAlert('Por favor, ingresa una URL válida.', 'warning');
            return;
        }

        if (this.gallery.children.length >= CONFIG.gallery.maxImages) {
            this.showAlert(`Máximo ${CONFIG.gallery.maxImages} imágenes permitidas.`, 'warning');
            return;
        }

        if (!this.isValidImageUrl(imageUrl)) {
            this.showAlert('Por favor, ingresa una URL de imagen válida (jpg, png, gif, webp).', 'error');
            return;
        }

        this.createImageElement(imageUrl);
        this.urlInput.value = '';
    }

    isValidImageUrl(url) {
        try {
            const urlObj = new URL(url);
            const validExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp'];
            const pathname = urlObj.pathname.toLowerCase();
            return validExtensions.some(ext => pathname.endsWith(ext));
        } catch {
      return false;
        }
    }

    createImageElement(url) {
        const imgContainer = document.createElement('div');
        imgContainer.className = 'gallery-item';
        imgContainer.style.position = 'relative';

        const img = document.createElement('img');
        img.src = url;
        img.alt = 'Imagen de la galería';
        img.style.width = '100%';
        img.style.height = CONFIG.gallery.defaultImageSize;
        img.style.objectFit = 'cover';
        img.style.borderRadius = '8px';
        img.style.cursor = 'pointer';
        img.style.transition = 'all 0.3s ease';

        img.addEventListener('click', () => this.selectImage(imgContainer, img));
        img.addEventListener('error', () => this.handleImageError(imgContainer));

        imgContainer.appendChild(img);
        this.gallery.appendChild(imgContainer);

        // Animación de entrada
        imgContainer.style.opacity = '0';
        imgContainer.style.transform = 'scale(0.8)';
        setTimeout(() => {
            imgContainer.style.opacity = '1';
            imgContainer.style.transform = 'scale(1)';
        }, 100);
    }

    selectImage(container, img) {
        // Remover selección anterior
        if (this.selectedImage) {
            this.selectedImage.classList.remove('selected');
        }

        // Seleccionar nueva imagen
        this.selectedImage = container;
        container.classList.add('selected');
        img.style.border = '3px solid #8e24aa';
        img.style.boxShadow = '0 0 15px rgba(142, 36, 170, 0.5)';
    }

    removeSelectedImage() {
        if (!this.selectedImage) {
            this.showAlert('No hay ninguna imagen seleccionada para eliminar.', 'warning');
            return;
        }

        this.selectedImage.style.opacity = '0';
        this.selectedImage.style.transform = 'scale(0.8)';
        
        setTimeout(() => {
            this.selectedImage.remove();
            this.selectedImage = null;
        }, 300);
    }

    handleImageError(container) {
        container.innerHTML = '<div class="error-placeholder">Error al cargar imagen</div>';
        container.style.background = '#f8f9fa';
        container.style.display = 'flex';
        container.style.alignItems = 'center';
        container.style.justifyContent = 'center';
        container.style.color = '#6c757d';
        container.style.fontSize = '0.9rem';
    }

    showAlert(message, type = 'info') {
        // Crear elemento de alerta
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.style.position = 'fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        alert.style.minWidth = '300px';
        
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alert);

        // Auto-remover después de 3 segundos
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 3000);
    }
}

// ===== VALIDADOR DE FORMULARIOS =====
class FormValidator {
    constructor() {
        this.form = document.getElementById('registrationForm');
        this.submitBtn = document.getElementById('submitButton');
        this.resetBtn = document.getElementById('resetButton');
        
        if (this.form) {
            this.init();
        }
    }

    init() {
        this.setupFields();
        this.setupEventListeners();
    }

    setupFields() {
        this.fields = {
            name: {
                input: document.getElementById('name'),
                error: document.getElementById('nameError'),
                validator: (value) => this.validateName(value)
            },
            email: {
                input: document.getElementById('email'),
                error: document.getElementById('emailError'),
                validator: (value) => this.validateEmail(value)
            },
            password: {
                input: document.getElementById('password'),
                error: document.getElementById('passwordError'),
                validator: (value) => this.validatePassword(value)
            },
            confirmPassword: {
                input: document.getElementById('confirmPassword'),
                error: document.getElementById('confirmPasswordError'),
                validator: (value) => this.validateConfirmPassword(value)
            },
            age: {
                input: document.getElementById('age'),
                error: document.getElementById('ageError'),
                validator: (value) => this.validateAge(value)
            }
        };
    }

    setupEventListeners() {
        // Event listeners para validación en tiempo real
        Object.values(this.fields).forEach(field => {
            if (field.input) {
                field.input.addEventListener('input', () => this.validateField(field));
                field.input.addEventListener('blur', () => this.validateField(field));
            }
        });

        // Event listeners para botones
        if (this.submitBtn) {
            this.submitBtn.addEventListener('click', (e) => this.handleSubmit(e));
        }
        if (this.resetBtn) {
            this.resetBtn.addEventListener('click', () => this.resetForm());
        }
    }

    validateName(value) {
        if (value.length < CONFIG.validation.minNameLength) {
            return `El nombre debe tener al menos ${CONFIG.validation.minNameLength} caracteres.`;
        }
        return null;
    }

    validateEmail(value) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(value)) {
            return 'Formato de correo electrónico inválido.';
        }
        return null;
    }

    validatePassword(value) {
        if (value.length < CONFIG.validation.minPasswordLength) {
            return `La contraseña debe tener al menos ${CONFIG.validation.minPasswordLength} caracteres.`;
        }
        return null;
    }

    validateConfirmPassword(value) {
        const password = this.fields.password.input.value;
        if (value !== password) {
            return 'Las contraseñas no coinciden.';
        }
        return null;
    }

    validateAge(value) {
        const age = parseInt(value);
        if (isNaN(age) || age < CONFIG.validation.minAge) {
            return `Debes ser mayor de ${CONFIG.validation.minAge} años.`;
        }
        return null;
    }

    validateField(field) {
        const value = field.input.value;
        const error = field.validator(value);
        
        if (error) {
            this.showFieldError(field, error);
      return false;
    } else {
            this.clearFieldError(field);
      return true;
    }
  }

    showFieldError(field, message) {
        field.input.classList.add('invalid');
        field.input.classList.remove('valid');
        if (field.error) {
            field.error.textContent = message;
            field.error.style.display = 'block';
        }
    }

    clearFieldError(field) {
        field.input.classList.remove('invalid');
        field.input.classList.add('valid');
        if (field.error) {
            field.error.style.display = 'none';
        }
    }

    validateForm() {
        let isValid = true;
        Object.values(this.fields).forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        return isValid;
    }

    updateSubmitButton() {
        if (this.submitBtn) {
            const isValid = this.validateForm();
            this.submitBtn.disabled = !isValid;
        }
    }

    handleSubmit(e) {
        e.preventDefault();
        
        if (!this.validateForm()) {
            this.showAlert('Por favor, corrige los errores en el formulario.', 'error');
            return;
        }

        // Simular envío
        this.showAlert('¡Formulario enviado con éxito!', 'success');
        this.resetForm();
    }

    resetForm() {
        Object.values(this.fields).forEach(field => {
            field.input.value = '';
            this.clearFieldError(field);
        });
        if (this.submitBtn) {
            this.submitBtn.disabled = true;
        }
    }

    showAlert(message, type = 'info') {
        // Usar la misma función de alerta que GalleryManager
        const gallery = new GalleryManager();
        gallery.showAlert(message, type);
    }
}

// ===== CATÁLOGO DINÁMICO =====
class ProductCatalog {
    constructor() {
        this.productList = document.getElementById('product-list');
        this.addBtn = document.getElementById('add-product');
        this.products = [
            { nombre: 'Vestido Elegante', talla: 'M', precio: '$39.99' },
            { nombre: 'Blusa Casual', talla: 'S', precio: '$19.99' },
            { nombre: 'Jean Clásico', talla: 'L', precio: '$49.99' }
        ];
        
        if (this.productList && this.addBtn) {
            this.init();
        }
    }

    init() {
        this.renderProducts();
        this.addBtn.addEventListener('click', () => this.addRandomProduct());
    }

    renderProducts() {
        this.productList.innerHTML = '';
        
        this.products.forEach((product, index) => {
    const li = document.createElement('li');
            li.className = 'product-item fade-in';
    li.innerHTML = `
                <div>
                    <div class="product-name">${product.nombre}</div>
                    <div class="product-description">Talla: ${product.talla}</div>
                </div>
                    <div class="product-price">${product.precio}</div>
            `;
            
            // Animación de entrada escalonada
            li.style.animationDelay = `${index * 0.1}s`;
            
            this.productList.appendChild(li);
        });
    }

    addRandomProduct() {
        const clothingTypes = ['Vestido', 'Blusa', 'Jean', 'Falda', 'Top'];
        const sizes = ['S', 'M', 'L', 'XL'];
        const colors = ['Negro', 'Blanco', 'Azul', 'Rosa', 'Verde'];
        
        const randomType = clothingTypes[Math.floor(Math.random() * clothingTypes.length)];
        const randomSize = sizes[Math.floor(Math.random() * sizes.length)];
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        const randomPrice = (20 + Math.random() * 50).toFixed(2);

  const newProduct = {
            nombre: `${randomColor} ${randomType}`,
            talla: randomSize,
            precio: `$${randomPrice}`
        };
        
        this.products.push(newProduct);
        this.renderProducts();
        
        // Scroll suave al nuevo producto
        const lastItem = this.productList.lastElementChild;
        lastItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    new GalleryManager();
    new FormValidator();
    new ProductCatalog();
    
    // Agregar animaciones de entrada
    const elements = document.querySelectorAll('.hero-section, .categories-section, .video-section, .gallery-section, .subscription-section, .catalog-section, .measurements-section');
    elements.forEach((element, index) => {
        element.classList.add('fade-in');
        element.style.animationDelay = `${index * 0.2}s`;
    });
    
    // Smooth scroll para enlaces internos
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    console.log('🎉 Caprichos Store - Script cargado correctamente');
});

// ===== UTILIDADES GLOBALES =====
window.CaprichosStore = {
    GalleryManager,
    FormValidator,
    ProductCatalog,
    CONFIG
};