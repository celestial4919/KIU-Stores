from django.shortcuts import render, get_object_or_404, redirect
from .forms import StudentSignUpForm
from .models import Product, User  # Make sure User is imported here
from .models import Product, CartItem, User, ProductImage
from django.contrib.auth.decorators import login_required
from .forms import ProductForm 
from .models import Product, User, Review
from .forms import BusinessOnboardingForm
from .models import BusinessApplication, Message, Report
from django.db.models import Q


# 2. The Product Details Page
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(pk=pk)[:4]
    
    return render(request, 'marketplace/product_detail.html', {
        'product': product,
        'related_products': related_products 
    })
    


# 3. The Store Profile Page
def vendor_store(request, pk):
    vendor = get_object_or_404(User, pk=pk)
    products = Product.objects.filter(vendor=vendor)
    return render(request, 'marketplace/vendor_store.html', {'vendor': vendor, 'products': products})


def signup_view(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') # Once they sign up, send them to login
    else:
        form = StudentSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def search_view(request):
    query = request.GET.get('q')
    results = Product.objects.none() # Start with an empty list
    
    if query:
        # icontains makes it case-insensitive (Search for 'nike' finds 'Nike')
        results = Product.objects.filter(title__icontains=query) | \
                  Product.objects.filter(description__icontains=query)
    
    return render(request, 'marketplace/search_results.html', {
        'results': results, 
        'query': query
    })


def home(request):
    # 1. Get the 'category' from the URL (e.g., /?category=electronics)
    category_slug = request.GET.get('category')
    
    # 2. Start with all products
    products = Product.objects.all()

    # 3. If a category was clicked, filter the products
    if category_slug and category_slug != 'all':
        # This assumes you have a 'category' field in your Product model
        products = products.filter(category__slug=category_slug)

    context = {
        'products': products,
        'active_category': category_slug or 'all' # Pass this to highlight the active pill
    }
    return render(request, 'marketplace/home.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        # Updating standard fields
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        user.location = request.POST.get('location')
        user.bio = request.POST.get('bio')
        
        # Updating Vendor-specific fields if applicable
        if user.is_student_seller or user.is_official_store:
            user.store_name = request.POST.get('store_name')
            user.business_specialty = request.POST.get('business_specialty')
            user.portfolio_url = request.POST.get('portfolio_url')

        # Handle Image Upload (Cloudinary)[cite: 2]
        if request.FILES.get('image'):
            user.image = request.FILES.get('image')
        
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'marketplace/profile.html')

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Calculate the total price
    total = sum(item.total_price() for item in cart_items)
    
    # Group items by vendor for the UI
    # We can do this easily in the template or here
    return render(request, 'marketplace/cart.html', {
        'cart_items': cart_items,
        'total': total,
    })

@login_required
def remove_from_cart(request, item_id):
    # We use get_object_or_404 for safety
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')    

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    # Adding a success message so they know it worked
    from django.contrib import messages
    messages.success(request, f"{product.title} added to your cart!")
    
    return redirect('home') # Keep them shopping!   

from django.shortcuts import render, redirect

def become_vendor_landing(request):
    """Renders the Celestial landing page with the registration form."""
    return render(request, 'marketplace/become_vendor.html')

def create_store_logic(request):
    """Processes the form and pushes them to the Terms and Conditions."""
    if request.method == 'POST':
        # Temporarily store form data in the session so we don't lose it
        request.session['temp_store_data'] = {
            'store_name': request.POST.get('store_name'),
            'whatsapp': request.POST.get('whatsapp'),
            'category': request.POST.get('category'),
        }
        # Redirect to the Terms and Conditions page as planned
        return redirect('terms_and_conditions')
    return redirect('become_vendor') 

# In views.py
def terms_and_conditions(request):
    """Shows the commission rules and the final 'Accept' button."""
    return render(request, 'marketplace/terms_and_conditions.html')

def final_onboarding_step(request):
    """Actually saves the vendor to the database after they accept terms."""
    # Pull the stored data
    data = request.session.get('temp_store_data')
    
    if data:
        # Update the user profile
        user = request.user
        user.store_name = data['store_name']
        user.whatsapp_number = data['whatsapp']
        user.is_student_seller = True # Or official based on logic
        user.save()
        
        # Clear the session now that we're done
        del request.session['temp_store_data']
        
        return redirect('vendor_dashboard')
        

    
def final_onboarding_step(request):
    """The final step: Moves data from session to Database."""
    if request.method == 'POST':
        # 1. Grab the temporary data we stored earlier
        data = request.session.get('temp_store_data')
        
        if not data:
            messages.error(request, "Session expired. Please start over.")
            return redirect('become_vendor')
        
        # 2. Update the user model (Assuming these fields exist)
        user = request.user
        user.store_name = data['store_name']
        user.whatsapp_number = data['whatsapp']
        user.is_vendor = True  # Officially a seller now!
        
        # Determine if they are Official or Student based on category or choice
        if data['category'] == 'Services' or data['store_name'].lower().find('official') != -1:
            user.is_official_store = True
        else:
            user.is_student_seller = True
            
        user.save()
        
        # 3. Clean up the session
        del request.session['temp_store_data']
        
        # 4. Success message & Redirect to Dashboard
        messages.success(request, f"Welcome to the Forge, {user.store_name}!")
        return redirect('vendor_dashboard') 
        
    return redirect('become_vendor')

@login_required
def vendor_dashboard(request):
    """The command center for vendors to track sales and inventory."""
    
    # 1. Security Check: Only let vendors in
    if not request.user.is_vendor:
        messages.info(request, "Please register your store to access the dashboard.")
        return redirect('become_vendor')
        
    # 2. Fetch all products belonging to this specific user[cite: 2, 3]
    products = Product.objects.filter(vendor=request.user)
    
    # 3. Calculate "Celestial Balance"
    # For now, we use a placeholder. Soon, we'll sum up completed orders.
    total_earnings = 0  # This will be: Order.objects.filter(vendor=user, status='completed').sum()
    threshold = 10000
    
    # Logic for the progress bar
    if total_earnings > 0:
        progress = (total_earnings / threshold) * 100
        if progress > 100: progress = 100
    else:
        progress = 0
        
    context = {
        'products': products,
        'total_earnings': total_earnings,
        'threshold': threshold,
        'progress': progress,
        'is_eligible': total_earnings >= threshold
    }
    
    return render(request, 'marketplace/vendor_dashboard.html', context)

@login_required
def my_store_profile(request):
    """Fetches the vendor's own data to display on their public-facing 'My Store' page."""
    
    # 1. Security check: Only vendors should have a 'My Store' page[cite: 3]
    if not request.user.is_vendor:
        messages.warning(request, "You need to register as a vendor first!")
        return redirect('become_vendor')

    # 2. Get the logged-in user's products
    # We use 'request.user' because this is YOUR store
    my_products = Product.objects.filter(vendor=request.user).order_by('-created_at')
    
    # 3. Get reviews (using the related_name 'reviews' we added to the model)
    # We'll handle the empty case in the template
    my_reviews = request.user.reviews.all().order_by('-created_at')

    context = {
        'vendor': request.user, # This gives us access to .working_hours, .location, etc.
        'products': my_products,
        'reviews': my_reviews,
    }
    
    return render(request, 'marketplace/my_store_profile.html', context)

@login_required
def add_product(request):
    if not request.user.is_vendor:
        return redirect('become_vendor')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES) # request.FILES is for the image!
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user  # Secretly link it to your account
            product.save()
            images = request.FILES.getlist('extra_images')
            for img in images:
                ProductImage.objects.create(product=product, image=img)
            messages.success(request, f"{product.title} is now live on KIU Stores!")
            return redirect('vendor_dashboard')
    else:
        form = ProductForm()
    
    return render(request, 'marketplace/add_product.html', {'form': form})

@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, vendor=request.user)
    if request.method == 'POST':
        # passing 'instance=product' tells Django to update the existing item instead of creating a new one
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save() # The save() method in models.py will handle the price markup update
            messages.success(request, f"{product.title} updated successfully!")
            return redirect('vendor_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'marketplace/edit_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, vendor=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('vendor_dashboard')
    # If they just click the link, show a confirmation page
    return render(request, 'marketplace/delete_confirm.html', {'product': product})

def privacy_policy(request):
    return render(request, 'marketplace/privacy.html')

@login_required
def settings_page(request):
    user = request.user
    if request.method == 'POST':
        # 1. Update Profile Info
        user.store_name = request.POST.get('store_name')
        user.phone_number = request.POST.get('phone_number')
        user.bio = request.POST.get('bio')
        user.location = request.POST.get('location')

        # 2. Update Technical Preferences
        user.data_saver = 'data_saver' in request.POST
        user.dark_mode = 'dark_mode' in request.POST
        user.is_invisible = 'is_invisible' in request.POST
        
        if request.FILES.get('profile_image'):
            user.image = request.FILES.get('profile_image')
            
        user.save()
        messages.success(request, "Settings updated successfully!")
        return redirect('settings_page')
        
    return render(request, 'marketplace/settings.html')

from django.shortcuts import render, get_object_or_404
from .models import Product, User # Ensure User is imported since it's your vendor model

def store_detail(request, vendor_id):
    # Fetch the vendor or return a 404 if they don't exist
    vendor = get_object_or_404(User, id=vendor_id)
    
    # Filter products to show only those belonging to this vendor
    products = Product.objects.filter(vendor=vendor).order_by('-created_at')
    
    context = {
        'vendor': vendor,
        'products': products,
    }
    return render(request, 'marketplace/store_detail.html', context)

def about_view(request):
    return render(request, 'marketplace/about.html')  

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name, email=email, subject=subject, message=message
        )
        
        messages.success(request, "Your message has been sent! We'll get back to you shortly.")
        return redirect('contact')
        
    return render(request, 'marketplace/contact.html')  

@login_required
def toggle_follow(request, vendor_id):
    vendor = get_object_or_404(User, id=vendor_id)
    if request.user != vendor: # Prevent following yourself
        if vendor in request.user.following.all():
            request.user.following.remove(vendor)
            messages.info(request, f"Unfollowed {vendor.store_name}")
        else:
            request.user.following.add(vendor)
            messages.success(request, f"Now following {vendor.store_name}!")
    
    # Redirects back to exactly where the user was scrolling
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def followed_stores_view(request):
    # Get all vendors the user follows
    stores = request.user.following.all()
    
    # Get all products belonging to those followed vendors
    # We order by '-id' to show the newest items first
    followed_products = Product.objects.filter(vendor__in=stores).order_by('-id')

    return render(request, 'marketplace/followed_stores.html', {
        'stores': stores,
        'followed_products': followed_products
    })



@login_required
def business_onboarding_view(request):
    # Check if the user has already applied to prevent duplicates
    existing_application = BusinessApplication.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        form = BusinessOnboardingForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            # Redirect to a success page or back to dashboard with a message
            return render(request, 'marketplace/onboarding_success.html') 
    else:
        form = BusinessOnboardingForm()

    return render(request, 'registration/business_onboarding.html', {
        'form': form,
        'existing_application': existing_application
    })

@login_required
def send_message(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                product=product,
                sender=request.user,
                receiver=product.vendor,
                content=content
            )
            return redirect('inbox')
    return redirect('product_detail', pk=product_id)

@login_required
def inbox(request):
    # Get all messages where the user is either the sender or receiver
    messages = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).order_by('-timestamp')
    return render(request, 'marketplace/inbox.html', {'messages': messages})

@login_required
def chat_thread(request, product_id, other_user_id):
    product = get_object_or_404(Product, id=product_id)
    other_user = get_object_or_404(User, id=other_user_id)
    
    # Fetch all messages involving both users regarding this product
    chat_messages = Message.objects.filter(
        product=product
    ).filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')

    # Mark messages received by the current user as read
    chat_messages.filter(receiver=request.user, is_read=False).update(is_read=True)

    return render(request, 'marketplace/chat_thread.html', {
        'product': product,
        'other_user': other_user,
        'chat_messages': chat_messages
    })

@login_required
def report_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        reason = request.POST.get('reason')
        description = request.POST.get('description')
        
        Report.objects.create(
            product=product,
            reporter=request.user,
            reason=reason,
            description=description
        )
        messages.success(request, "Thank you. Our team will investigate this listing.")
        return redirect('product_detail', pk=product.id)
    
    return render(request, 'marketplace/report_form.html', {'product': product})
