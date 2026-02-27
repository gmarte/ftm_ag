'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { fetchWithAuth } from '@/lib/api';
import ParentDashboard from './ParentDashboard';
import KidDashboard from './KidDashboard';

interface Profile {
    id: number;
    user: {
        username: string;
        first_name: string;
        last_name: string;
    };
    role: 'PARENT' | 'KID';
    points: number;
}

export default function DashboardPage() {
    const router = useRouter();
    const [profile, setProfile] = useState<Profile | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadProfile = async () => {
            try {
                const res = await fetchWithAuth('/profiles/me/');
                if (!res.ok) throw new Error('Unauthenticated');
                const data = await res.json();
                setProfile(data);
            } catch (err) {
                router.push('/login');
            } finally {
                setLoading(false);
            }
        };
        loadProfile();
    }, [router]);

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen bg-gray-50 dark:bg-gray-900">
                <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
            </div>
        );
    }

    if (!profile) return null;

    return (
        <main className="min-h-screen bg-gray-50/30 dark:bg-gray-900/30">
            {profile.role === 'PARENT' ? (
                <ParentDashboard profile={profile} />
            ) : (
                <KidDashboard profile={profile} />
            )}
        </main>
    );
}
