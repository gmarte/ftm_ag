'use client';

import { useEffect, useState } from 'react';
import { fetchWithAuth } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LogOut, Smile, Frown, Check, X } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function ParentDashboard({ profile: initialProfile }: { profile: any }) {
    const router = useRouter();
    const [kids, setKids] = useState<any[]>([]);
    const [redemptions, setRedemptions] = useState<any[]>([]);
    const [profile, setProfile] = useState(initialProfile);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            try {
                const [profilesRes, redemptionsRes] = await Promise.all([
                    fetchWithAuth('/profiles/'),
                    fetchWithAuth('/redemptions/')
                ]);
                const profilesData = await profilesRes.json();
                const redemptionsData = await redemptionsRes.json();

                setKids(profilesData.filter((p: any) => p.role === 'KID'));
                setRedemptions(redemptionsData.filter((r: any) => r.status === 'PENDING'));
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.push('/login');
    };

    const logBehavior = async (kidId: number, actionType: 'GOOD' | 'BAD') => {
        try {
            const res = await fetchWithAuth(`/profiles/${kidId}/log_behavior/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action_type: actionType })
            });
            if (res.ok) {
                const data = await res.json();
                setKids(kids.map(k => k.id === kidId ? { ...k, points: data.new_points } : k));
            }
        } catch (e) {
            console.error(e);
        }
    };

    const processRedemption = async (redemptionId: number, action: 'approve' | 'reject') => {
        try {
            const res = await fetchWithAuth(`/redemptions/${redemptionId}/process/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action })
            });

            if (res.ok) {
                // Remove from pending list
                setRedemptions(redemptions.filter(r => r.id !== redemptionId));

                // If rejected, we must refund points in UI so we re-fetch the kids data
                if (action === 'reject') {
                    const profilesRes = await fetchWithAuth('/profiles/');
                    const profilesData = await profilesRes.json();
                    setKids(profilesData.filter((p: any) => p.role === 'KID'));
                }
            }
        } catch (e) {
            console.error(e);
        }
    };

    if (loading) return null;

    return (
        <div className="space-y-12 pb-24 max-w-6xl mx-auto p-4 md:p-8">
            {/* Top Navbar */}
            <nav className="bg-white/80 backdrop-blur-md border border-gray-200 px-4 py-3 dark:bg-gray-900/80 dark:border-gray-800 rounded-full flex justify-between items-center shadow-sm sticky top-4 z-50 transition-all duration-300">
                <div className="flex items-center gap-3">
                    <img className="w-10 h-10 rounded-full border-2 border-primary object-cover"
                        src={`https://ui-avatars.com/api/?name=${profile.user.first_name || profile.user.username}&background=3b82f6&color=fff`}
                        alt="Parent Avatar" />
                    <span className="text-lg font-bold text-gray-800 dark:text-gray-100 hidden sm:inline-block">
                        {profile.user.first_name || profile.user.username}'s Dashboard
                    </span>
                </div>
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={handleLogout} className="text-gray-400 hover:text-red-500 rounded-full">
                        <LogOut className="h-5 w-5" />
                    </Button>
                </div>
            </nav>

            {/* Hero Section */}
            <div className="relative bg-gradient-to-br from-blue-500 to-indigo-600 rounded-[2rem] p-8 md:p-12 mb-10 overflow-hidden shadow-lg shadow-blue-500/30">
                <div className="absolute top-0 right-0 -mt-10 -mr-10 w-48 h-48 bg-white opacity-20 rounded-full blur-2xl"></div>
                <div className="absolute bottom-0 left-0 -mb-10 -ml-10 w-32 h-32 bg-white opacity-20 rounded-full blur-xl"></div>

                <div className="relative z-10 text-white">
                    <h1 className="text-3xl md:text-5xl font-extrabold drop-shadow-sm mb-2 tracking-tight">Family Overview</h1>
                    <p className="text-blue-100 font-medium text-lg opacity-90">Manage redemptions and track your children's progress.</p>
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">

                {/* Kids Overview Column */}
                <div className="lg:col-span-2 space-y-6">
                    <h2 className="text-2xl font-black tracking-tight text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="p-2 bg-blue-500/10 rounded-lg text-blue-500">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
                        </span>
                        Child Profiles
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {kids.map((kid: any) => (
                            <div key={kid.id} className="bg-white dark:bg-gray-800 rounded-3xl shadow-sm hover:shadow-md border border-gray-100 dark:border-gray-700 overflow-hidden transition-all duration-300">
                                <div className="p-6">
                                    <div className="flex items-center gap-4 mb-6">
                                        <img src={`https://ui-avatars.com/api/?name=${kid.user.first_name || kid.user.username}&background=FB923C&color=fff&size=64`}
                                            alt={kid.user.username}
                                            className="w-16 h-16 rounded-full border-4 border-orange-50 object-cover shadow-sm" />
                                        <div>
                                            <h3 className="text-xl font-bold text-gray-900 dark:text-white capitalize">{kid.user.first_name || kid.user.username}</h3>
                                        </div>
                                    </div>

                                    <div className="bg-gradient-to-r from-orange-50 to-amber-50 dark:from-gray-700/50 dark:to-gray-700/30 rounded-2xl p-4 mb-6 text-center border border-orange-100/50">
                                        <span className="block text-xs uppercase tracking-widest text-orange-400 font-bold mb-1">Current Points</span>
                                        <div className="text-4xl font-extrabold text-orange-500 drop-shadow-sm">{kid.points}</div>
                                    </div>

                                    <div className="flex justify-between items-center bg-gray-50 dark:bg-gray-700/50 rounded-xl p-2 px-3 mb-4">
                                        <Button onClick={() => logBehavior(kid.id, 'GOOD')}
                                            className="h-10 w-12 bg-green-100 hover:bg-green-200 text-green-700 rounded-lg shadow-none active:scale-95 transition-all">
                                            <Smile className="w-6 h-6" />
                                        </Button>
                                        <span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest text-center leading-tight">Quick<br />Log</span>
                                        <Button onClick={() => logBehavior(kid.id, 'BAD')}
                                            className="h-10 w-12 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg shadow-none active:scale-95 transition-all">
                                            <Frown className="w-6 h-6" />
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Pending Redemptions Column */}
                <div className="space-y-6">
                    <h2 className="text-2xl font-black tracking-tight text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="p-2 bg-orange-500/10 rounded-lg text-orange-500">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" /></svg>
                        </span>
                        Pending Requests
                    </h2>

                    <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
                        {redemptions.length > 0 ? (
                            <ul className="divide-y divide-gray-50 dark:divide-gray-700/50">
                                {redemptions.map((redemption: any) => (
                                    <li key={redemption.id} className="p-5 flex flex-col gap-4 hover:bg-gray-50/50 dark:hover:bg-gray-700/20 transition-colors">
                                        <div className="flex items-center gap-4">
                                            <div className="w-12 h-12 rounded-2xl bg-orange-100 dark:bg-orange-500/20 flex items-center justify-center text-2xl drop-shadow-sm shrink-0">
                                                {redemption.reward.icon || "🎁"}
                                            </div>
                                            <div className="leading-tight">
                                                <div className="text-sm text-gray-500 mb-0.5">
                                                    <span className="font-bold text-gray-800 dark:text-gray-200 capitalize">{redemption.user.first_name || redemption.user.username}</span> requested:
                                                </div>
                                                <div className="font-bold text-orange-500">
                                                    {redemption.reward.title}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex gap-2 w-full mt-2">
                                            <Button onClick={() => processRedemption(redemption.id, 'approve')}
                                                className="flex-1 bg-teal-400 hover:bg-teal-500 text-white font-bold rounded-xl shadow-sm shadow-teal-400/20">
                                                <Check className="w-4 h-4 mr-1" /> Approve
                                            </Button>
                                            <Button onClick={() => processRedemption(redemption.id, 'reject')}
                                                variant="outline"
                                                className="flex-1 border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700 hover:border-red-300 font-bold rounded-xl">
                                                <X className="w-4 h-4 mr-1" /> Reject
                                            </Button>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <div className="p-10 text-center flex flex-col items-center justify-center min-h-[250px] bg-gray-50/50 dark:bg-gray-800/50">
                                <div className="text-4xl mb-3 opacity-50">✨</div>
                                <h3 className="text-lg font-bold text-gray-800 dark:text-gray-300">All caught up!</h3>
                                <p className="text-gray-500 text-sm mt-1">No pending rewards to review at this time.</p>
                            </div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
}
