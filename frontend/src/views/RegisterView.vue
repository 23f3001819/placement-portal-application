<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-2 col-lg-12">
        <div class="card shadow-sm">
          <div class="card-body p-4">
            <h3 class="text-center mb-4">Create an Account</h3>

            <form @submit.prevent="handleRegister">
              
              <div class="mb-4 text-center">
                <div class="btn-group" role="group">
                  <input type="radio" class="btn-check" id="roleStudent" value="student" v-model="role">
                  <label class="btn btn-outline-primary" for="roleStudent">Student</label>

                  <input type="radio" class="btn-check" id="roleCompany" value="company" v-model="role">
                  <label class="btn btn-outline-primary" for="roleCompany">Company</label>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Full Name / Company Name</label>
                <input type="text" class="form-control" v-model="form.name" required>
              </div>

              <div class="mb-3">
                <label class="form-label">Email address</label>
                <input type="email" class="form-control" v-model="form.email" required>
              </div>

              <div class="mb-3">
                <label class="form-label">Password</label>
                <input type="password" class="form-control" v-model="form.password" required>
              </div>

              <div v-if="role === 'student'">
                <div class="mb-3">
                  <label class="form-label">Branch</label>
                  <select class="form-select" v-model="form.branch" required>
                    <option value="" disabled>Select your branch</option>
                    <option value="MechE">MechE</option>
                    <option value="ProdE">ProdE</option>
                    <option value="EE">EE</option>
                    <option value="ETCE">ETCE</option>
                    <option value="CSE">CSE</option>
                    <option value="DS">DS</option>
                  </select>
                </div>
                <div class="mb-3">
                  <label class="form-label">CGPA</label>
                  <input type="number" step="0.01" min="0" max="10" class="form-control" v-model="form.cgpa" required>
                </div>
                <div class="mb-4">
                  <label class="form-label">Upload Resume (PDF)</label>
                  <input type="file" class="form-control" accept=".pdf" @change="handleFileChange" required>
                </div>
              </div>

              <div v-if="role === 'company'">
                <div class="mb-3">
                  <label class="form-label">HR Contact (Phone)</label>
                  <input type="text" class="form-control" v-model="form.hr_con" required>
                </div>
                <div class="mb-4">
                  <label class="form-label">Website</label>
                  <input type="url" class="form-control" v-model="form.webs" placeholder="https://company.com" required>
                </div>
              </div>

              <div class="d-grid">
                <button type="submit" class="btn btn-primary">Register</button>
              </div>

              <div class="text-center mt-3">
                <small>Already have an account? <router-link to="/login">Login here</router-link></small>
              </div>

            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const role = ref('student');
const resumeFile = ref(null);

const form = reactive({
  name: '',
  email: '',
  password: '',
  branch: '',
  cgpa: '',
  hr_con: '',
  webs: ''
});


const handleFileChange = (event) => {
  resumeFile.value = event.target.files[0];
};

const handleRegister = async () => {
  try {

    const payload = new FormData();
    
    payload.append('role', role.value);
    payload.append('name', form.name);
    payload.append('email', form.email);
    payload.append('password', form.password);

    if (role.value === 'student') {
      payload.append('branch', form.branch);
      payload.append('cgpa', form.cgpa);
      if (resumeFile.value) {
        payload.append('resume', resumeFile.value);
      }
    } else if (role.value === 'company') {
      payload.append('hr_con', form.hr_con);
      payload.append('webs', form.webs);
    }

    const response = await fetch('http://localhost:5000/api/register', {
      method: 'POST',
      body: payload
    });

    const result = await response.json();

    if (response.ok) {
      alert(result.message || 'Registration successful!');
      router.push('/login'); 
    } else {
      alert(result.message || 'Registration failed.');
    }
  } catch (error) {
    console.error('Registration Error:', error);
    alert('A network error occurred while trying to register.');
  }
};
</script>