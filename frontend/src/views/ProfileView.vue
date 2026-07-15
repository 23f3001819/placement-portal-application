<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authstore.js';

const router = useRouter();
const auth_store = useAuthStore();

const roles = computed(() => auth_store.getUserRoles());
const isStudent = computed(() => roles.value.includes('student'));
const isCompany = computed(() => roles.value.includes('company'));
const isAdmin = computed(() => roles.value.includes('admin'));

const isLoading = ref(true);
const isSaving = ref(false);
const successMessage = ref('');
const errorMessage = ref('');


const profileData = ref({
    name: '',
    email: '',
    password: '',
    
    branch: '',
    cgpa: 0,
    resume_path: '',
    status: null,
    
    hr_con: '',
    webs: ''
});

const selectedFile = ref(null);

const fetchProfile = async () => {
    try {
        isLoading.value = true;
        errorMessage.value = '';
        successMessage.value = '';
        
        let url = '';
        if (isStudent.value) {
            url = 'http://127.0.0.1:5000/api/student/profile';
        } else if (isCompany.value) {
            url = 'http://127.0.0.1:5000/api/company/profile';
        } else if (isAdmin.value) {
            url = 'http://127.0.0.1:5000/api/admin/profile';
        } else {
            errorMessage.value = 'Invalid user role.';
            isLoading.value = false;
            return;
        }

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': auth_store.getAuthToken() || ''
            }
        });
        
        const data = await response.json();
        if (response.ok) {
            profileData.value = { ...profileData.value, ...data, password: '' };
        } else {
            errorMessage.value = data.message || 'Failed to load profile data.';
        }
    } catch (error) {
        console.error('Error fetching profile:', error);
        errorMessage.value = 'A network error occurred while loading your profile.';
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
    fetchProfile();
});

const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
        if (file.type !== 'application/pdf') {
            alert('Only PDF files are allowed for resumes.');
            event.target.value = '';
            selectedFile.value = null;
            return;
        }
        selectedFile.value = file;
    }
};

const updateProfile = async () => {
    try {
        isSaving.value = true;
        errorMessage.value = '';
        successMessage.value = '';

        let url = '';
        let method = 'PUT';
        let headers = {
            'Authorization': auth_store.getAuthToken() || ''
        };
        let body = null;

        if (isStudent.value) {
            url = 'http://127.0.0.1:5000/api/student/profile';
            
            const formData = new FormData();
            formData.append('name', profileData.value.name);
            formData.append('email', profileData.value.email);
            if (profileData.value.password) {
                formData.append('password', profileData.value.password);
            }
            formData.append('branch', profileData.value.branch);
            formData.append('cgpa', profileData.value.cgpa);
            if (selectedFile.value) {
                formData.append('resume', selectedFile.value);
            }
            body = formData;
            
        } else if (isCompany.value) {
            url = 'http://127.0.0.1:5000/api/company/profile';
            headers['Content-Type'] = 'application/json';
            const payload = {
                name: profileData.value.name,
                email: profileData.value.email,
                hr_con: profileData.value.hr_con,
                webs: profileData.value.webs
            };
            if (profileData.value.password) {
                payload.password = profileData.value.password;
            }
            body = JSON.stringify(payload);
        } else if (isAdmin.value) {
            url = 'http://127.0.0.1:5000/api/admin/profile';
            headers['Content-Type'] = 'application/json';
            const payload = {
                name: profileData.value.name,
                email: profileData.value.email
            };
            if (profileData.value.password) {
                payload.password = profileData.value.password;
            }
            body = JSON.stringify(payload);
        }

        const response = await fetch(url, {
            method,
            headers,
            body
        });

        const data = await response.json();
        if (response.ok) {
            successMessage.value = data.message || 'Profile updated successfully!';
            
            profileData.value.password = '';
            
            if (data.user && data.user.email) {
                auth_store.setUserCred(auth_store.getAuthToken(), {
                    email: data.user.email,
                    role: roles.value
                });
            }
            
            await fetchProfile();
        } else {
            errorMessage.value = data.message || 'Failed to update profile.';
        }
    } catch (error) {
        console.error('Error updating profile:', error);
        errorMessage.value = 'A network error occurred while saving profile changes.';
    } finally {
        isSaving.value = false;
    }
};

const getStudentStatusBadge = (status) => {
    if (status === 0) return { label: 'Actively Seeking', class: 'bg-info text-dark' };
    if (status === 1) return { label: 'Placed / Selected', class: 'bg-success text-white' };
    if (status === 2) return { label: 'Suspended / Blacklisted', class: 'bg-danger text-white' };
    return { label: 'Unknown', class: 'bg-secondary text-white' };
};

const getCompanyStatusBadge = (status) => {
    if (status === 1) return { label: 'Active', class: 'bg-success text-white' };
    if (status === 0) return { label: 'Suspended / Blacklisted', class: 'bg-danger text-white' };
    return { label: 'Unknown', class: 'bg-secondary text-white' };
};
</script>

<template>
    <div class="container my-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <!-- Heading and Navigation back to dashboard -->
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2>Edit Profile Details</h2>
                    <RouterLink 
                        v-if="isStudent" 
                        to="/student" 
                        class="btn btn-outline-secondary btn-sm"
                    >
                        <i class="bi bi-arrow-left me-1"></i> Back to Dashboard
                    </RouterLink>
                    <RouterLink 
                        v-else-if="isCompany" 
                        to="/company" 
                        class="btn btn-outline-secondary btn-sm"
                    >
                        <i class="bi bi-arrow-left me-1"></i> Back to Dashboard
                    </RouterLink>
                    <RouterLink 
                        v-else-if="isAdmin" 
                        to="/admin" 
                        class="btn btn-outline-secondary btn-sm"
                    >
                        <i class="bi bi-arrow-left me-1"></i> Back to Dashboard
                    </RouterLink>
                </div>

                <div v-if="isLoading" class="text-center my-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2 text-muted">Loading profile details...</p>
                </div>

                <div v-else class="card shadow-lg border-0 rounded-3 overflow-hidden">
                    <!-- Glassmorphism header based on user role -->
                    <div 
                        class="card-header py-4 text-white" 
                        :class="{
                            'bg-gradient bg-primary': isStudent,
                            'bg-gradient bg-success': isCompany,
                            'bg-gradient bg-dark': isAdmin
                        }"
                    >
                        <h4 class="mb-1 text-center text-white">{{ profileData.name || 'Your Profile' }}</h4>
                        <p class="mb-0 text-center text-white-50 small">
                            Role: {{ isStudent ? 'Student' : isCompany ? 'Company Partner' : 'System Administrator' }}
                        </p>
                    </div>

                    <div class="card-body p-4">
                        <!-- Custom Alert Messages -->
                        <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
                            <i class="bi bi-check-circle-fill me-2"></i> {{ successMessage }}
                            <button type="button" class="btn-close" @click="successMessage = ''"></button>
                        </div>
                        
                        <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
                            <i class="bi bi-exclamation-triangle-fill me-2"></i> {{ errorMessage }}
                            <button type="button" class="btn-close" @click="errorMessage = ''"></button>
                        </div>

                        <!-- Blacklist warnings (Visual status feedback) -->
                        <div v-if="isStudent && profileData.status === 2" class="alert alert-danger py-3 text-center mb-4">
                            <h5 class="alert-heading mb-1"><i class="bi bi-x-octagon-fill me-2"></i>Account Suspended</h5>
                            <p class="mb-0 small">Your student profile has been blacklisted. You cannot participate in placement drives. Contact Placement Cell to resolve.</p>
                        </div>
                        <div v-if="isCompany && profileData.status === 0" class="alert alert-danger py-3 text-center mb-4">
                            <h5 class="alert-heading mb-1"><i class="bi bi-x-octagon-fill me-2"></i>Account Suspended</h5>
                            <p class="mb-0 small">Your company account has been deactivated. You cannot post or manage placement drives. Contact Placement Admin.</p>
                        </div>

                        <!-- Main Form -->
                        <form @submit.prevent="updateProfile">
                            
                            <!-- Role Badges & Status Information (Disabled / Non-Editable Section) -->
                            <div class="row mb-4 bg-light p-3 rounded mx-0 align-items-center">
                                <div class="col-sm-6">
                                    <span class="text-muted small d-block">Account Status</span>
                                    <span 
                                        v-if="isStudent" 
                                        :class="['badge', getStudentStatusBadge(profileData.status).class, 'px-3 py-2 mt-1']"
                                    >
                                        {{ getStudentStatusBadge(profileData.status).label }}
                                    </span>
                                    <span 
                                        v-else-if="isCompany" 
                                        :class="['badge', getCompanyStatusBadge(profileData.status).class, 'px-3 py-2 mt-1']"
                                    >
                                        {{ getCompanyStatusBadge(profileData.status).label }}
                                    </span>
                                    <span 
                                        v-else 
                                        class="badge bg-success px-3 py-2 mt-1"
                                    >
                                        Super User (Active)
                                    </span>
                                </div>
                                <div class="col-sm-6 text-sm-end mt-2 mt-sm-0 text-muted small">
                                    <i class="bi bi-info-circle me-1"></i> Status fields are managed strictly by Administrators and Placement Protocols.
                                </div>
                            </div>

                            <!-- Common Fields -->
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="name" class="form-label">Full Name</label>
                                    <input 
                                        type="text" 
                                        id="name" 
                                        v-model="profileData.name" 
                                        class="form-control" 
                                        required
                                    />
                                </div>
                                
                                <div class="col-md-6 mb-3">
                                    <label for="email" class="form-label">Email Address</label>
                                    <input 
                                        type="email" 
                                        id="email" 
                                        v-model="profileData.email" 
                                        class="form-control" 
                                        required
                                    />
                                </div>
                            </div>

                            <div class="mb-4">
                                <label for="password" class="form-label">Change Password</label>
                                <input 
                                    type="password" 
                                    id="password" 
                                    v-model="profileData.password" 
                                    class="form-control" 
                                    placeholder="Leave blank to keep current password"
                                    autocomplete="new-password"
                                />
                                <div class="form-text">If you don't wish to change your password, keep this field empty.</div>
                            </div>

                            <!-- Student Specific Fields -->
                            <div v-if="isStudent" class="border-top pt-4 mt-4">
                                <h5 class="text-primary mb-3">Student Academic Details</h5>
                                
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label for="branch" class="form-label">Academic Branch</label>
                                        <select id="branch" v-model="profileData.branch" class="form-select" required>
                                            <option value="">Select Branch</option>
                                            <option value="MechE">MechE</option>
                                            <option value="ProdE">ProdE</option>
                                            <option value="EE">EE</option>
                                            <option value="ETCE">ETCE</option>
                                            <option value="CSE">CSE</option>
                                            <option value="DS">DS</option>
                                        </select>
                                    </div>
                                    
                                    <div class="col-md-6 mb-3">
                                        <label for="cgpa" class="form-label">Cumulative CGPA</label>
                                        <input 
                                            type="number" 
                                            id="cgpa" 
                                            v-model="profileData.cgpa" 
                                            class="form-control" 
                                            min="0" 
                                            max="10" 
                                            step="0.01" 
                                            required
                                        />
                                    </div>
                                </div>

                                <div class="mb-3">
                                    <label for="resume" class="form-label">Upload Resume (PDF only)</label>
                                    <input 
                                        type="file" 
                                        id="resume" 
                                        class="form-control" 
                                        accept=".pdf" 
                                        @change="handleFileChange"
                                    />
                                    <div class="form-text">Uploading a new file will overwrite the existing resume.</div>
                                </div>

                                <div v-if="profileData.resume_path" class="mb-3 p-3 bg-light rounded d-flex justify-content-between align-items-center">
                                    <div>
                                        <i class="bi bi-file-earmark-pdf-fill text-danger fs-4 me-2"></i>
                                        <span class="small text-muted">Current Resume: </span>
                                        <strong class="small">{{ profileData.resume_path.split('/').pop() }}</strong>
                                    </div>
                                    <a 
                                        :href="`http://127.0.0.1:5000/${profileData.resume_path}`" 
                                        target="_blank" 
                                        class="btn btn-sm btn-outline-primary"
                                    >
                                        <i class="bi bi-eye"></i> View Resume
                                    </a>
                                </div>
                            </div>

                            <!-- Company Specific Fields -->
                            <div v-if="isCompany" class="border-top pt-4 mt-4">
                                <h5 class="text-success mb-3">Company Details</h5>
                                
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label for="hr_con" class="form-label">HR Contact Number</label>
                                        <input 
                                            type="text" 
                                            id="hr_con" 
                                            v-model="profileData.hr_con" 
                                            class="form-control" 
                                            pattern="[0-9]{10}"
                                            title="10-digit mobile number"
                                            required
                                        />
                                    </div>
                                    
                                    <div class="col-md-6 mb-3">
                                        <label for="webs" class="form-label">Corporate Website</label>
                                        <input 
                                            type="url" 
                                            id="webs" 
                                            v-model="profileData.webs" 
                                            class="form-control" 
                                            placeholder="https://example.com"
                                            required
                                        />
                                    </div>
                                </div>
                            </div>

                            <!-- Submit button -->
                            <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4 pt-3 border-top">
                                <button 
                                    type="submit" 
                                    class="btn px-4" 
                                    :class="{
                                        'btn-primary': isStudent,
                                        'btn-success': isCompany,
                                        'btn-dark': isAdmin
                                    }"
                                    :disabled="isSaving"
                                >
                                    <span v-if="isSaving" class="spinner-border spinner-border-sm me-2" role="status"></span>
                                    {{ isSaving ? 'Saving Changes...' : 'Save Profile Details' }}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.bg-gradient {
    background-size: 100% 100%;
}
</style>
