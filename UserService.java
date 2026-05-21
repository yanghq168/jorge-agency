package com.jorge.ai.demo.service;

import com.jorge.ai.demo.entity.LoginLog;
import com.jorge.ai.demo.entity.User;
import com.jorge.ai.demo.repository.LoginLogRepository;
import com.jorge.ai.demo.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {

    private final UserRepository userRepository;
    private final LoginLogRepository loginLogRepository;
    private final PasswordEncoder passwordEncoder;

    public Page<User> getAllUsers(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("id").ascending());
        return userRepository.findAll(pageable);
    }

    public User getUserById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("User not found: " + id));
    }

    public User getUserByUsername(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("User not found: " + username));
    }

    @Transactional
    public User updateUser(Long id, String email, String role, Boolean enabled) {
        User user = getUserById(id);
        if (email != null && !email.isBlank()) {
            user.setEmail(email);
        }
        if (role != null && !role.isBlank()) {
            user.setRole(role);
        }
        if (enabled != null) {
            user.setEnabled(enabled);
        }
        return userRepository.save(user);
    }

    @Transactional
    public void deleteUser(Long id) {
        User user = getUserById(id);
        userRepository.delete(user);
        log.info("User deleted: {}", id);
    }

    @Transactional
    public User createUserByAdmin(String username, String password, String email, String role) {
        if (userRepository.existsByUsername(username)) {
            throw new RuntimeException("Username already exists: " + username);
        }
        if (userRepository.existsByEmail(email)) {
            throw new RuntimeException("Email already exists: " + email);
        }

        User user = User.builder()
                .username(username)
                .password(passwordEncoder.encode(password))
                .email(email)
                .role(role != null ? role : "USER")
                .enabled(true)
                .build();

        return userRepository.save(user);
    }

    public Page<LoginLog> getAllLoginLogs(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("loginTime").descending());
        return loginLogRepository.findAll(pageable);
    }

    public Map<String, Object> getStats() {
        long totalUsers = userRepository.count();
        long adminCount = userRepository.countByRole("ADMIN");

        LocalDateTime todayStart = LocalDate.now().atStartOfDay();
        long todayLogins = loginLogRepository.countByLoginTimeAfter(todayStart);
        long failedLogins = loginLogRepository.countBySuccessAndLoginTimeAfter(false, todayStart);
        long totalLogins = loginLogRepository.count();

        Map<String, Object> stats = new HashMap<>();
        stats.put("totalUsers", totalUsers);
        stats.put("adminCount", adminCount);
        stats.put("todayLogins", todayLogins);
        stats.put("failedLogins", failedLogins);
        stats.put("totalLogins", totalLogins);
        return stats;
    }
}
