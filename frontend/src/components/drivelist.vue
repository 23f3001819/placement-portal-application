<script setup>
import { RouterLink } from 'vue-router';

defineProps({
  items: {
    type: Array,
    required: true
  }
});

const formatStatus = (status) => {
  if (status === 0) return { label: 'Pending Approval', class: 'bg-warning text-dark' };
  if (status === 1) return { label: 'Active', class: 'bg-success' };
  if (status === 2) return { label: 'Ended', class: 'bg-secondary' };
  return { label: 'Unknown', class: 'bg-light text-dark' };
};

const formatDate = (dateStr) => {
  try {
    return new Date(dateStr).toLocaleString();
  } catch (e) {
    return dateStr;
  }
};
</script>

<template>
  <div class="table-responsive">
    <table class="table table-striped table-hover align-middle">
      <thead class="table-dark">
        <tr>
          <th>ID</th>
          <th>Company ID</th>
          <th>Role</th>
          <th>Description</th>
          <th>Pay (in LPA)</th>
          <th>Deadline</th>
          <th>Status</th>
          <th class="text-center">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.comp_id }}</td>
          <td><strong>{{ item.job_role }}</strong></td>
          <td>{{ item.job_desc || '-' }}</td>
          <td>{{ item.job_pay }} LPA</td>
          <td>{{ formatDate(item.deadline) }}</td>
          <td>
            <span :class="['badge', formatStatus(item.status).class]">
              {{ formatStatus(item.status).label }}
            </span>
          </td>
          <td class="text-center">
            <div class="btn-group" role="group">
              <RouterLink 
                :to="{ name: 'editdrive', params: { id: item.id } }" 
                class="btn btn-sm btn-outline-primary"
                title="Edit Drive"
              >
                <i class="bi bi-pencil-fill me-1"></i>Edit
              </RouterLink>
              <RouterLink 
                :to="{ name: 'driveapplicants', params: { id: item.id } }" 
                class="btn btn-sm btn-outline-info"
                title="View Applicants"
              >
                <i class="bi bi-people-fill me-1"></i>Applicants
              </RouterLink>
            </div>
          </td>
        </tr>
        
        <tr v-if="items.length === 0">
          <td colspan="8" class="text-center text-muted py-4">No placement drives found.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>