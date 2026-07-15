<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authstore.js';

const props = defineProps({
  id: {
    type: [String, Number],
    required: true
  }
});

const router = useRouter();
const auth_store = useAuthStore();

const jobRole = ref('');
const jobDesc = ref('');
const branchCriteria = ref('');
const cgpaCriteria = ref('');
const jobCtc = ref('');
const deadline = ref('');
const status = ref(0);

const errorMessage = ref('');
const isLoading = ref(true);

onMounted(async () => {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/drives/${props.id}`, {
            method: 'GET',
            headers: {
                'Authorization': auth_store.getAuthToken() || ''
            }
        });

        const data = await response.json();

        if (response.ok) {
            jobRole.value = data.job_role;
            jobDesc.value = data.job_desc;
            cgpaCriteria.value = data.cgpa_c;
            jobCtc.value = data.job_ctc;
            status.value = data.status;

            if (Array.isArray(data.branch_c)) {
                branchCriteria.value = data.branch_c.join(', ');
            } else {
                branchCriteria.value = data.branch_c || '';
            }

            if (data.deadline) {
                deadline.value = data.deadline.slice(0, 16);
            }
        } else {
            errorMessage.value = data.message || "Failed to load drive details.";
        }
    } catch (error) {
        console.error("Error fetching drive details:", error);
        errorMessage.value = "Failed to load drive details due to a network error.";
    } finally {
        isLoading.value = false;
    }
});

const updateDrive = async () => {
    if (!jobRole.value || !branchCriteria.value || !cgpaCriteria.value || !jobCtc.value || !deadline.value) {
        errorMessage.value = "Please fill in all required fields.";
        return;
    }

    const formattedDeadline = new Date(deadline.value).toISOString();
    const branchList = branchCriteria.value.split(',').map(s => s.trim()).filter(s => s.length > 0);

    const payload = {
        job_role: jobRole.value,
        job_desc: jobDesc.value,
        branch_c: branchList,
        cgpa_c: parseFloat(cgpaCriteria.value),
        job_ctc: parseFloat(jobCtc.value),
        deadline: formattedDeadline,
        status: status.value
    };

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/drives/${props.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': auth_store.getAuthToken() || ''
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message || "Drive updated successfully.");
            router.push({ name: 'company' });
        } else {
            errorMessage.value = data.message || "Failed to update drive.";
        }
    } catch (error) {
        console.error("Network error:", error);
        errorMessage.value = "A network error occurred. Please try again.";
    }
};
</script>

<template>
    <div class="container mt-5" style="max-width: 600px;">
        <h2 class="mb-4">Edit Placement Drive</h2>
        
        <div v-if="isLoading" class="text-center my-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Fetching drive details...</p>
        </div>

        <div v-else>
            <div v-if="errorMessage" class="alert alert-danger">
                {{ errorMessage }}
            </div>

            <form @submit.prevent="updateDrive">
                
                <div class="mb-3">
                    <label for="jobRole" class="form-label">Job Role *</label>
                    <input type="text" class="form-control" id="jobRole" v-model="jobRole" required>
                </div>

                <div class="mb-3">
                    <label for="jobDesc" class="form-label">Job Description</label>
                    <textarea class="form-control" id="jobDesc" rows="3" v-model="jobDesc"></textarea>
                </div>

                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="jobCtc" class="form-label">Pay / CTC (in LPA) *</label>
                        <input type="number" step="0.1" class="form-control" id="jobCtc" v-model="jobCtc" required>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label for="deadline" class="form-label">Application Deadline *</label>
                        <input type="datetime-local" class="form-control" id="deadline" v-model="deadline" required>
                    </div>
                </div>

                <h5 class="mt-4 border-bottom pb-2">Eligibility Criteria</h5>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="cgpaCriteria" class="form-label">Minimum CGPA *</label>
                        <input type="number" step="0.1" min="0" max="10" class="form-control" id="cgpaCriteria" v-model="cgpaCriteria" required>
                    </div>

                    <div class="col-md-6 mb-3">
                        <label for="branchCriteria" class="form-label">Eligible Branches *</label>
                        <input type="text" class="form-control" id="branchCriteria" placeholder="e.g. CSE, IT or ALL" v-model="branchCriteria" required>
                    </div>
                </div>

                <!-- If status is active or ended, let company manage the status (e.g. close the drive early) -->
                <div v-if="status > 0" class="mb-3">
                    <label for="status" class="form-label">Drive Status</label>
                    <select class="form-select" id="status" v-model="status">
                        <option :value="1">Active</option>
                        <option :value="2">Ended</option>
                    </select>
                    <div class="form-text">Active drives accept applications until deadline. Ended drives are closed.</div>
                </div>

                <div class="d-flex justify-content-between mt-4">
                    <RouterLink to="/company" class="btn btn-secondary">Cancel</RouterLink>
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                </div>
                
            </form>
        </div>
    </div>
</template>
